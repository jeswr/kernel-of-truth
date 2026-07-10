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


# =====================================================================
# B″ — nsk1 Stage-0 KEYED internal-channel probe at R3, phase:"exploratory"
# ---------------------------------------------------------------------
# EXECUTES docs/next/nsk1-bprime2-spec.md (Fable, runner-ready; ASM-0200..0204;
# ZERO design decisions left to the runner). Control-unpassable REDESIGN of B′.
# This entrypoint is APPENDED; the g2/g2b/g2c/g2d/bprime code and every shared
# helper above are byte-untouched. It reuses the verified plumbing:
#   * form-2 (entity) TEXT-ONLY prompts + D_bridge donor = _build_specs_bprime
#     (byte-identical to _build_specs_g2b f2 branch) — extended only with D_top.
#   * _score_entity scorer byte-verbatim; _bp_wilson / _bp_binom_sf_ge /
#     _bp_sattolo byte-verbatim; the hooksmoke-verified residual read/write path
#     (hidden_states[k] = input of decoder module k; pre-hook on layers[ℓt]).
# NEW mechanism (spec §2 DECISION): ADDITIVE NORM-MATCHED CONTRASTIVE injection
#   h_p ← h_p + s·α·‖h_p‖·Δ̂v  (NOT B′'s replacement transplant), where
#   Δ̂v = unit(v_top − v_bridge), v_* harvested at the donor answer-slot name.
# Read-out (spec §2/§3 Step 6): source-keyed counterfactual-pair discrimination,
#   paired teacher-forced logprob margin m(v)=lp(top|v)−lp(bridge|v); success bit
#   = m(+)>m(−); ties/non-finite = failure. COIN control (null anchor, ≤0.5 by
#   construction) + ROLE control (mechanism separator) both from the deranged arm.
# Host R3 = SmolLM2-1.7B-Instruct, commit-pinned; A10G fp32; all 958 covered
# CLUTRR entity-form items; greedy 16-tok gens; every row phase:"exploratory".
#
#   .venv/bin/modal run poc/modal/modal_nsk1_g2.py::bprime2 --dry-plan   # $0
#   .venv/bin/modal run poc/modal/modal_nsk1_g2.py::bprime2              # A10G
# =====================================================================

BPRIME2_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"          # R3 (ASM-0040)
BPRIME2_PIN = "31b70e2e869a7173562077fd711b654946d38674"        # commit pin (spec §2, ABORT otherwise)
BPRIME2_SEED = 20260712        # σ₂ derangement / C100 / 300-cap / coin (spec §2)
BPRIME2_ALPHA_LADDER = [0.125, 0.25, 0.5, 1.0]  # α calibration ladder (spec §3 Step 5)
BPRIME2_FLOOR = 0.70           # keyed-accuracy floor (spec §2/§5)
BPRIME2_Z_PASS = 2.5427        # PASS-side one-sided Wilson LB, 1−0.05/9 (spec §4)
BPRIME2_Z_KILL = 1.6449        # KILL-side one-sided Wilson UB, 95% (spec §4)
BPRIME2_Z_CTRL = 2.7730        # control-validity two-sided per side, 1−0.05/18 (spec §4)
BPRIME2_SWEEP_CAP = 300        # Swept cap (spec §3 Step 3)
BPRIME2_C100 = 100             # correct subsample size (spec §3 Step 3)
BPRIME2_CCAL = 32              # calibration subsample (first 32 of C100) (spec §3 Step 5)
BPRIME2_BATCH = 16             # GPU mini-batch (memory-safe; OOM auto-halves)
BPRIME2_WALL_CAP_S = 19800     # soft in-container wall guard (5.5 h) < Modal timeout


def _bprime2_grid(L: int):
    """9-cell grid (spec §2 DECISION / §3 Step 2). lay(f)=min(L−1,max(1,round(f·L))).
    ℓh∈{lay(1/2),lay(2/3),lay(5/6)} × ℓt∈{lay(1/3),lay(1/2),lay(2/3)}.
    Pivot=(lay(2/3),lay(1/2)). At L=24: ℓh∈{12,16,20}, ℓt∈{8,12,16}, pivot=(16,12).
    Cell order: pivot first, then row-major (ℓh asc, ℓt asc)."""
    def lay(f):
        return min(L - 1, max(1, int(round(f * L))))
    LH = sorted({lay(1 / 2), lay(2 / 3), lay(5 / 6)})
    LT = sorted({lay(1 / 3), lay(1 / 2), lay(2 / 3)})
    pivot = (lay(2 / 3), lay(1 / 2))
    rowmajor = [(h, t) for h in LH for t in LT]
    assert len(rowmajor) <= 9, "ABORT: |cells|=%d > 9" % len(rowmajor)
    assert pivot in rowmajor, "ABORT: pivot %s not in grid" % (pivot,)
    ordered = [pivot] + [c for c in rowmajor if c != pivot]
    return LH, LT, pivot, ordered


def _build_specs_bprime2():
    """Reuse _build_specs_bprime for the 958 form-2 TEXT-ONLY prompts + the
    D_bridge donor (byte-identical to g2b f2 + the run-1/g2b feedback renderer),
    then add the D_top donor (spec §3 Step 0). ABORTs on any build-gate breach.
    Both donors = 'Note: the <rs> of <base> is <NAME>.' differing ONLY in the
    answer-slot name (top vs bridge). B′'s gold-not-in-feedback assert is WAIVED
    for D_top ONLY — donor text never enters the model as prompt text; only its
    harvested activations are injected (Law 1 holds). Pure/local (torch-free)."""
    base = _build_specs_bprime()  # authoritative prompt + feedback(=D_bridge) + names
    lex = json.loads((_ROOT / "data/nsk1-clutrr/lexicon.json").read_text())
    rel_surface = {v: k for k, v in lex["relations"].items()}

    def _rows(path, sf):
        for line in (_ROOT / path).read_text().splitlines():
            if not line.strip():
                continue
            it = json.loads(line)
            if sf is not None and it.get("stratum") != sf:
                continue
            yield it

    src = list(_rows("data/nsk1-clutrr/items.jsonl", "covered")) + \
        list(_rows("data/nsk1-clutrr/headroom.jsonl", None))
    assert len(src) == len(base) == 958, \
        "ABORT: src=%d base=%d (expected 958)" % (len(src), len(base))

    out = []
    for it, bs in zip(src, base):
        assert it["item_id"] == bs["item_id"], \
            "ABORT: order mismatch %s vs %s" % (it["item_id"], bs["item_id"])
        item_lex = it["lexicon"]
        surfaces = list(item_lex.values())
        assert len(item_lex) == 3 and len({s.lower() for s in surfaces}) == 3, \
            "ABORT: item %s not 3-name pairwise-distinct" % it["item_id"]
        subj_urn = it["hop1"]["subject"]
        bridge_urn = it["hop1_bridge"]
        base_surface = item_lex[subj_urn]
        top_urns = [u for u in item_lex if u not in (subj_urn, bridge_urn)]
        assert len(top_urns) == 1, "ABORT: item %s no unique chain-top" % it["item_id"]
        top_surface = item_lex[top_urns[0]]
        bridge_surface = item_lex[bridge_urn]
        rs = rel_surface[it["hop1"]["rel"]]
        prefix = "Note: the %s of %s is " % (rs, base_surface)
        d_bridge = prefix + bridge_surface + "."
        d_top = prefix + top_surface + "."
        # reuse fidelity: reused feedback must BE the D_bridge donor, byte-for-byte
        assert d_bridge == bs["feedback"], \
            "ABORT: D_bridge != reused feedback (%s)" % it["item_id"]
        assert (bs["bridge_surface"] == bridge_surface and bs["gold_top"] == top_surface
                and bs["base"] == base_surface), "ABORT: name field drift (%s)" % it["item_id"]
        # donors differ ONLY in the name slot (identical prefix + '.' suffix)
        assert d_top == prefix + top_surface + "." and d_bridge == prefix + bridge_surface + ".", \
            "ABORT: donor template drift (%s)" % it["item_id"]
        assert d_top[:len(prefix)] == d_bridge[:len(prefix)] and d_top[-1] == d_bridge[-1] == ".", \
            "ABORT: donors differ outside name slot (%s)" % it["item_id"]
        out.append({
            "item_id": bs["item_id"], "prompt": bs["prompt"],
            "d_top": d_top, "d_bridge": d_bridge,
            "top_surface": top_surface, "bridge_surface": bridge_surface,
            "gold_top": top_surface, "base": base_surface, "surfaces": surfaces,
        })
    assert len(out) == 958, "ABORT: built %d != 958" % len(out)
    return out


def _bprime2_coin_bit(item_id, lh, lt, seed=BPRIME2_SEED):
    """Deterministic, auditable, content-independent per-(item,cell) coin bit
    (spec §2 DECISION seeds)."""
    import hashlib
    key = "%d|%s|%d|%d" % (seed, item_id, lh, lt)
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) & 1


class _B2Abort(Exception):
    """Raised in-body for a spec ABORT that maps to INSTRUMENT-INVALID."""


# ----------------------------------------------------- GPU body (torch, remote)
def _bprime2_body(model_id, specs, bprime_text_correct, batch_size, wall_cap_s):
    import traceback
    try:
        return _bprime2_body_impl(model_id, specs, bprime_text_correct,
                                  batch_size, wall_cap_s)
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        print("BPRIME2 ERROR:", repr(e))
        print(tb)
        return {"aborted": True, "abort_reason": "EXCEPTION: %s" % repr(e),
                "traceback": tb, "rows": [], "summary": {}, "swept_item_ids": [],
                "c100_item_ids": [], "per_cell": {}, "per_cell_c100": {},
                "cells": [], "completed_cells": [], "secondaries": {}}


def _bprime2_body_impl(model_id, specs, bprime_text_correct, batch_size, wall_cap_s):
    import re
    import time
    import math
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    n = len(specs)
    tok = AutoTokenizer.from_pretrained(model_id, revision=BPRIME2_PIN)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, revision=BPRIME2_PIN, torch_dtype=torch.float32)
    model.to("cuda").eval()
    L = int(model.config.num_hidden_layers)
    d_model = int(model.config.hidden_size)
    commit = getattr(model.config, "_commit_hash", None)
    # spec §2: resolved commit MUST equal the pin (ABORT otherwise)
    if commit is not None and commit != BPRIME2_PIN:
        return {"aborted": True,
                "abort_reason": "COMMIT_PIN_MISMATCH got=%s want=%s" % (commit, BPRIME2_PIN),
                "rows": [], "summary": {"model_commit": commit}, "swept_item_ids": [],
                "c100_item_ids": [], "per_cell": {}, "per_cell_c100": {}, "cells": [],
                "completed_cells": [], "secondaries": {}}
    assert L >= 12, "ABORT: L=%d < 12" % L
    layers = model.model.layers
    LH, LT, pivot, cells = _bprime2_grid(L)
    assert len(cells) <= 9, "ABORT: |cells|=%d > 9" % len(cells)
    print("[bp2] model=%s L=%d d=%d commit=%s" % (model_id, L, d_model, commit))
    print("[bp2] LH=%s LT=%s pivot=%s cells=%s" % (LH, LT, pivot, cells))

    # ---- additive norm-matched pre-hook (edits INPUT of module ℓt at pos w) ----
    hook_state = {"vec": None, "wpos": None}  # vec=[bs,d]=s·α·Δ̂v ; wpos=[bs] long

    def add_pre_hook(module, args, kwargs):
        st = hook_state
        if st["vec"] is None:
            return None
        hs = None
        where = None
        if len(args) > 0 and torch.is_tensor(args[0]) and args[0].dim() == 3:
            hs, where = args[0], "arg"
        elif torch.is_tensor(kwargs.get("hidden_states")):
            hs, where = kwargs["hidden_states"], "kw"
        if hs is None or hs.shape[1] <= 1:
            return None  # decode step (seq==1): prefill-only (spec §3 Step 5/6)
        hs = hs.clone()
        u = st["vec"].to(hs.dtype)          # [bs, d]
        wpos = st["wpos"]                    # [bs] long
        bs = hs.shape[0]
        rows = torch.arange(bs, device=hs.device)
        cur = hs[rows, wpos, :]              # [bs, d]
        nrm = cur.norm(dim=-1, keepdim=True)  # [bs, 1] = ‖h_p‖
        hs[rows, wpos, :] = cur + nrm * u   # h ← h + ‖h‖·(s·α·Δ̂v)
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

    def _mini(items):
        for a in range(0, len(items), batch_size):
            yield items[a:a + batch_size]

    def _gen_plain(id_lists):
        try:
            ii, am, maxlen = _pad_batch(id_lists)
            with torch.no_grad():
                out = model.generate(input_ids=ii, attention_mask=am,
                                     max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                                     num_beams=1, pad_token_id=tok.pad_token_id)
            return [tok.decode(out[r][maxlen:], skip_special_tokens=True)
                    for r in range(len(id_lists))]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(id_lists) == 1:
                raise
            h = len(id_lists) // 2
            return _gen_plain(id_lists[:h]) + _gen_plain(id_lists[h:])

    def _gen_add(id_lists, lt, vecs_signed):
        """Greedy 16-tok gen with the additive hook at layer lt, final prompt pos
        (prefill only). vecs_signed[r]=s·α·Δ̂v (unit dir). OOM->halve."""
        try:
            ii, am, maxlen = _pad_batch(id_lists)
            handle = None
            if lt is not None and vecs_signed is not None:
                hook_state["vec"] = torch.stack(vecs_signed).to("cuda")
                hook_state["wpos"] = torch.full((len(id_lists),), maxlen - 1,
                                                device="cuda", dtype=torch.long)
                handle = layers[lt].register_forward_pre_hook(add_pre_hook, with_kwargs=True)
            try:
                with torch.no_grad():
                    out = model.generate(input_ids=ii, attention_mask=am,
                                         max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                                         num_beams=1, pad_token_id=tok.pad_token_id)
            finally:
                if handle is not None:
                    handle.remove()
                hook_state["vec"] = None
                hook_state["wpos"] = None
            return [tok.decode(out[r][maxlen:], skip_special_tokens=True)
                    for r in range(len(id_lists))]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(id_lists) == 1:
                raise
            h = len(id_lists) // 2
            v1 = vecs_signed[:h] if vecs_signed is not None else None
            v2 = vecs_signed[h:] if vecs_signed is not None else None
            return _gen_add(id_lists[:h], lt, v1) + _gen_add(id_lists[h:], lt, v2)

    prompt_ids = [None] * n
    cand_ids = [None] * n  # per item: {'top': ids, 'bridge': ids}

    def _tf_lp(mb, cand_key, lt, vec_for):
        """Teacher-forced Σ logprob of candidate cand_key for each item idx in mb,
        under additive injection at layer lt (vec_for(i)=s·α·Δ̂v_i) at the last
        prompt-token position w=maxlen−len(cand)−1. lt/vec_for None => unhooked
        baseline. Returns list of lp. ASSERTs write-index; OOM->halve."""
        try:
            id_lists = [prompt_ids[i] + cand_ids[i][cand_key] for i in mb]
            clens = [len(cand_ids[i][cand_key]) for i in mb]
            ii, am, maxlen = _pad_batch(id_lists)
            wrows = [maxlen - clens[r] - 1 for r in range(len(mb))]
            for r, i in enumerate(mb):
                if int(ii[r, wrows[r]].item()) != prompt_ids[i][-1]:
                    raise _B2Abort("WRITE_INDEX_MISMATCH item=%s" % specs[i]["item_id"])
            handle = None
            if lt is not None and vec_for is not None:
                u = torch.stack([vec_for(i) for i in mb]).to("cuda")
                hook_state["vec"] = u
                hook_state["wpos"] = torch.tensor(wrows, device="cuda", dtype=torch.long)
                handle = layers[lt].register_forward_pre_hook(add_pre_hook, with_kwargs=True)
            try:
                with torch.no_grad():
                    out = model(input_ids=ii, attention_mask=am)
            finally:
                if handle is not None:
                    handle.remove()
                hook_state["vec"] = None
                hook_state["wpos"] = None
            logits = out.logits
            lps = []
            for r, i in enumerate(mb):
                w = wrows[r]
                cid = cand_ids[i][cand_key]
                lp = 0.0
                for j, tid in enumerate(cid):
                    lr = torch.log_softmax(logits[r, w + j, :].float(), dim=-1)
                    lp += float(lr[tid].item())
                lps.append(lp)
            del out, logits
            return lps
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(mb) == 1:
                raise
            h = len(mb) // 2
            return _tf_lp(mb[:h], cand_key, lt, vec_for) + _tf_lp(mb[h:], cand_key, lt, vec_for)

    def _has_any(g, surfaces):
        t = g.lower()
        return any(re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(x.lower()), t)
                   for x in surfaces)

    def _emit_cat(g, s):
        t = g.lower()
        pos = {}
        for role, name in (("top", s["top_surface"]), ("bridge", s["bridge_surface"]),
                           ("base", s["base"])):
            m = re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(name.lower()), t)
            if m:
                pos[role] = m.start()
        if not pos:
            return "none"
        first = min(pos, key=pos.get)
        return {"top": "top", "bridge": "bridge", "base": "other"}[first]

    def _row(**kw):
        base = {"phase": "exploratory", "gate": "BPRIME2", "host": "R3",
                "model": model_id, "surface": "clutrr", "form": "2"}
        base.update(kw)
        return base

    rows = []

    # =============== STEP 1: text-only pass (958 batched gens) ===================
    for i, s in enumerate(specs):
        prompt_ids[i] = _chat_ids(s["prompt"])
    text_only = [False] * n
    text_gen = [None] * n
    order = list(range(n))
    done = 0
    for mb in _mini(order):
        gens = _gen_plain([prompt_ids[i] for i in mb])
        for i, g in zip(mb, gens):
            s = specs[i]
            ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
            text_only[i] = ok
            text_gen[i] = g
        done += len(mb)
        if done % 160 == 0 or done == n:
            print("[bp2] step1 %d/%d acc_running=%.3f t=%.0fs"
                  % (done, n, sum(text_only[:done]) / max(1, done), time.time() - t0))
    acc_text = sum(text_only) / n
    headroom_ok = (0.05 <= acc_text <= 0.85) and (n >= 900)
    # repro gate vs B′ text-only correctness vector (spec §3 Step 1)
    repro_agree = 0
    repro_disagree = []
    for i, s in enumerate(specs):
        ref = bprime_text_correct.get(s["item_id"])
        if ref is not None and bool(text_only[i]) == bool(ref):
            repro_agree += 1
        elif ref is not None:
            repro_disagree.append(s["item_id"])
    print("[bp2] STEP1 acc_text=%.4f headroom_ok=%s repro_agree=%d/958"
          % (acc_text, headroom_ok, repro_agree))
    for i, s in enumerate(specs):
        rows.append(_row(item_id=s["item_id"], probe="text-only", cell=None,
                         arm=None, sign=None, alpha=None, coin=None,
                         lp_top=None, lp_bridge=None, gen=text_gen[i],
                         correct=bool(text_only[i]), emitted=None, gold=s["gold_top"]))

    summary = {
        "model": model_id, "model_commit": commit, "L": L, "d_model": d_model,
        "grid": {"LH": LH, "LT": LT, "pivot": list(pivot),
                 "cells_sweep_order": [list(c) for c in cells]},
        "alpha_ladder": BPRIME2_ALPHA_LADDER, "seed": BPRIME2_SEED,
        "coin_bit_recipe": "int(sha256('%d|item_id|lh|lt').hexdigest(),16)&1" % BPRIME2_SEED,
        "z": {"pass": BPRIME2_Z_PASS, "kill": BPRIME2_Z_KILL, "ctrl": BPRIME2_Z_CTRL},
        "floor": BPRIME2_FLOOR, "n_items": n, "n_scored": n,
        "acc_text_only": acc_text, "headroom_ok": bool(headroom_ok),
        "repro_agree": repro_agree, "repro_disagreements": repro_disagree,
        "batch_size": batch_size,
    }

    def _early(reason):
        summary.update({"aborted": True, "abort_reason": reason,
                        "elapsed_s": time.time() - t0})
        return {"aborted": True, "abort_reason": reason, "rows": rows,
                "summary": summary, "swept_item_ids": [], "c100_item_ids": [],
                "per_cell": {}, "per_cell_c100": {}, "cells": [list(c) for c in cells],
                "completed_cells": [], "secondaries": {}}

    if repro_agree < 910:
        return _early("REPRO_DRIFT repro_agree=%d<910" % repro_agree)
    if not headroom_ok:
        return _early("HEADROOM acc_text=%.4f n=%d" % (acc_text, n))

    # =============== STEP 3: sets, derangement, coins ===========================
    F = [i for i in range(n) if not text_only[i]]
    correct_idx = [i for i in range(n) if text_only[i]]
    if len(F) <= BPRIME2_SWEEP_CAP:
        swept = list(F)
    else:
        swept = sorted(_bp_random.Random(BPRIME2_SEED).sample(F, BPRIME2_SWEEP_CAP))
    if len(correct_idx) < BPRIME2_C100:
        return _early("C100_SHORT only %d correct (<%d)" % (len(correct_idx), BPRIME2_C100))
    c100 = sorted(_bp_random.Random(BPRIME2_SEED).sample(correct_idx, BPRIME2_C100))
    assert not (set(swept) & set(c100)), "ABORT: Swept∩C100 nonempty"
    c_cal = c100[:BPRIME2_CCAL]  # first 32 of C100 in ascending covered-set order
    m = len(swept)
    perm = _bp_sattolo(m, BPRIME2_SEED)
    assert all(perm[k] != k for k in range(m)), "ABORT: derangement has fixed point"
    sigma = {swept[k]: swept[perm[k]] for k in range(m)}
    print("[bp2] |F|=%d |Swept|=%d |C100|=%d |C_cal|=%d (σ₂ fixed-point-free)"
          % (len(F), m, len(c100), len(c_cal)))
    summary.update({"n_failures": len(F), "n_swept": m, "n_c100": len(c100),
                    "n_ccal": len(c_cal), "swept_is_full_F": len(F) <= BPRIME2_SWEEP_CAP,
                    "runner_operational_instantiations": [
                        "disc-c100 deranged arm: spec pins σ₂ over Swept only; the "
                        "reported-only (never gate-bearing) C100 deranged arm uses the "
                        "SAME pinned Sattolo operator (seed 20260712) over C100 order. "
                        "DISCLOSED for designer confirmation; affects no §5 gate/verdict."]})

    need = sorted(set(swept) | set(c100))
    for i in need:
        s = specs[i]
        for key, name in (("top", s["top_surface"]), ("bridge", s["bridge_surface"])):
            cid = tok(" " + name, add_special_tokens=False).input_ids
            assert len(cid) >= 1, "ABORT: empty cand ids (%s)" % s["item_id"]
            if cand_ids[i] is None:
                cand_ids[i] = {}
            cand_ids[i][key] = list(cid)

    aborted = False
    abort_reason = None
    partial = False
    partial_reason = None
    completed_cells = []
    per_cell = {}
    per_cell_c100 = {}
    baseline_margins = []
    secondaries = {}
    dhat = {}

    try:
        # ============ STEP 4: donor harvest (Δ̂v at ℓh∈LH) ======================
        def _last_name_tok(text, name, offsets):
            cstart = text.rfind(name)
            if cstart < 0:
                return None
            cend = cstart + len(name)
            found = None
            for ti, (a, b) in enumerate(offsets):
                if a == b:
                    continue
                if a < cend and b > cstart:
                    found = ti
            return found

        for i in need:
            s = specs[i]
            hv = {}
            for key, name, text in (("top", s["top_surface"], s["d_top"]),
                                    ("bridge", s["bridge_surface"], s["d_bridge"])):
                enc = tok(text, return_offsets_mapping=True)
                ti = _last_name_tok(text, name, enc["offset_mapping"])
                if ti is None:
                    raise _B2Abort("NAME_LOCATION donor=%s item=%s" % (key, s["item_id"]))
                idt = torch.tensor([enc["input_ids"]], device="cuda")
                with torch.no_grad():
                    fwd = model(idt, output_hidden_states=True)
                hv[key] = {lh: fwd.hidden_states[lh][0, ti, :].detach().float().clone()
                           for lh in LH}
                del fwd
            dv = {}
            for lh in LH:
                d = hv["top"][lh] - hv["bridge"][lh]
                nrm = float(d.norm())
                if not (nrm > 0):
                    raise _B2Abort("DELTA_ZERO item=%s lh=%d" % (s["item_id"], lh))
                dv[lh] = d / d.norm()
            dhat[i] = dv
        print("[bp2] donors harvested for %d items (no gen) t=%.0fs"
              % (len(need), time.time() - t0))

        # ============ STEP 5: α calibration (pivot cell, mechanical) ============
        plh, plt = pivot
        alpha_table = {}
        for a in BPRIME2_ALPHA_LADDER:
            nogen = 0
            total = 0
            for sgn in (1, -1):
                for mb in _mini(c_cal):
                    idl = [prompt_ids[i] for i in mb]
                    vecs = [a * sgn * dhat[i][plh] for i in mb]
                    gens = _gen_add(idl, plt, vecs)
                    for i, g in zip(mb, gens):
                        has = _has_any(g, specs[i]["surfaces"])
                        if not has:
                            nogen += 1
                        total += 1
                        rows.append(_row(item_id=specs[i]["item_id"], probe="calib",
                                         cell=[plh, plt], arm="real", sign=sgn,
                                         alpha=a, coin=None, lp_top=None, lp_bridge=None,
                                         gen=g, correct=None,
                                         emitted=("none" if not has else _emit_cat(g, specs[i])),
                                         gold=specs[i]["gold_top"]))
            alpha_table[a] = {"collapse": (nogen / total if total else 1.0),
                              "n": total}
        qualifying = [a for a in BPRIME2_ALPHA_LADDER if alpha_table[a]["collapse"] <= 0.10]
        alpha_star = max(qualifying) if qualifying else 0.125
        summary.update({"alpha_table": {("%g" % a): alpha_table[a] for a in BPRIME2_ALPHA_LADDER},
                        "alpha_star": alpha_star})
        print("[bp2] α table=%s α*=%g t=%.0fs"
              % ({("%g" % a): round(alpha_table[a]["collapse"], 3) for a in BPRIME2_ALPHA_LADDER},
                 alpha_star, time.time() - t0))

        # ============ STEP 6: GATE-BEARING margin sweep (Swept, pivot first) =====
        # drg_map: item_idx -> deranged donor item_idx. For the gate-bearing Swept
        # sweep this is σ₂ (spec §3, Sattolo over Swept, seed 20260712). For the
        # REPORTED-ONLY / never-gate-bearing disc-c100 arm the spec pins σ₂ over
        # Swept only, so we apply the SAME pinned Sattolo operator over the C100
        # order (DISCLOSED runner operational instantiation; touches no gate/verdict).
        def _run_disc(cell_items, cells_list, store, probe, gate_bearing, drg_map):
            for (lh, lt) in cells_list:
                if gate_bearing and (time.time() - t0 > wall_cap_s):
                    return "WALL_CAP during %s at cell %d_%d" % (probe, lh, lt)
                key = "%d_%d" % (lh, lt)
                acc = {"real": [], "coin": [], "role": [],
                       "real_ties": 0, "coin_ties": 0, "role_ties": 0,
                       "mdiff_real": [], "mdiff_role": [], "mdiff_coin": []}
                for mb in _mini(cell_items):
                    def _mgn(vecfn):
                        r = {}
                        for sgn in (1, -1):
                            vf = (lambda i, sgn=sgn, vecfn=vecfn:
                                  alpha_star * sgn * vecfn(i))
                            lpt = _tf_lp(mb, "top", lt, vf)
                            lpb = _tf_lp(mb, "bridge", lt, vf)
                            r[sgn] = (lpt, lpb)
                        return r
                    real = _mgn(lambda i: dhat[i][lh])
                    drg = _mgn(lambda i: dhat[drg_map[i]][lh])
                    for r_idx, i in enumerate(mb):
                        s = specs[i]
                        rp_t, rp_b = real[1][0][r_idx], real[1][1][r_idx]
                        rm_t, rm_b = real[-1][0][r_idx], real[-1][1][r_idx]
                        dp_t, dp_b = drg[1][0][r_idx], drg[1][1][r_idx]
                        dm_t, dm_b = drg[-1][0][r_idx], drg[-1][1][r_idx]
                        vals = [rp_t, rp_b, rm_t, rm_b, dp_t, dp_b, dm_t, dm_b]
                        if not all(math.isfinite(v) for v in vals):
                            raise _B2Abort("NAN_MARGINS item=%s cell=%s" % (s["item_id"], key))
                        mr_p = rp_t - rp_b
                        mr_m = rm_t - rm_b
                        md_p = dp_t - dp_b
                        md_m = dm_t - dm_b
                        b = _bprime2_coin_bit(s["item_id"], lh, lt)
                        real_bit = 1 if mr_p > mr_m else 0
                        role_bit = 1 if md_p > md_m else 0
                        coin_bit = (1 if md_p > md_m else 0) if b == 1 else (1 if md_m > md_p else 0)
                        acc["real"].append(real_bit)
                        acc["role"].append(role_bit)
                        acc["coin"].append(coin_bit)
                        if mr_p == mr_m:
                            acc["real_ties"] += 1
                        if md_p == md_m:
                            acc["role_ties"] += 1
                            acc["coin_ties"] += 1
                        acc["mdiff_real"].append(mr_p - mr_m)
                        acc["mdiff_role"].append(md_p - md_m)
                        acc["mdiff_coin"].append((md_p - md_m) if b == 1 else (md_m - md_p))
                        rows.append(_row(item_id=s["item_id"], probe=probe, cell=[lh, lt],
                                         arm="real", sign=1, alpha=alpha_star, coin=None,
                                         lp_top=rp_t, lp_bridge=rp_b, gen=None, correct=None,
                                         emitted=None, gold=s["gold_top"]))
                        rows.append(_row(item_id=s["item_id"], probe=probe, cell=[lh, lt],
                                         arm="real", sign=-1, alpha=alpha_star, coin=None,
                                         lp_top=rm_t, lp_bridge=rm_b, gen=None, correct=None,
                                         emitted=None, gold=s["gold_top"]))
                        rows.append(_row(item_id=s["item_id"], probe=probe, cell=[lh, lt],
                                         arm="drg", sign=1, alpha=alpha_star, coin=b,
                                         lp_top=dp_t, lp_bridge=dp_b, gen=None, correct=None,
                                         emitted=None, gold=s["gold_top"]))
                        rows.append(_row(item_id=s["item_id"], probe=probe, cell=[lh, lt],
                                         arm="drg", sign=-1, alpha=alpha_star, coin=b,
                                         lp_top=dm_t, lp_bridge=dm_b, gen=None, correct=None,
                                         emitted=None, gold=s["gold_top"]))
                store[key] = acc
                if gate_bearing:
                    completed_cells.append([lh, lt])
                print("[bp2] %s cell (%d,%d) done t=%.0fs" % (probe, lh, lt, time.time() - t0))
            return None

        stop = _run_disc(swept, cells, per_cell, "disc", True, sigma)
        if stop:
            partial, partial_reason = True, stop

        # ============ STEP 6 baselines: unhooked margins (Swept ∪ C100) =========
        if not partial:
            for mb in _mini(need):
                lpt = _tf_lp(mb, "top", None, None)
                lpb = _tf_lp(mb, "bridge", None, None)
                for r_idx, i in enumerate(mb):
                    s = specs[i]
                    if not (math.isfinite(lpt[r_idx]) and math.isfinite(lpb[r_idx])):
                        raise _B2Abort("NAN_BASELINE item=%s" % s["item_id"])
                    baseline_margins.append(lpt[r_idx] - lpb[r_idx])
                    rows.append(_row(item_id=s["item_id"], probe="baseline", cell=None,
                                     arm=None, sign=None, alpha=None, coin=None,
                                     lp_top=lpt[r_idx], lp_bridge=lpb[r_idx], gen=None,
                                     correct=None, emitted=None, gold=s["gold_top"]))
            print("[bp2] baselines done t=%.0fs" % (time.time() - t0))

        # ============ STEP 6 disc-c100 (reported-only, never gate-bearing) ======
        # σ over C100 order via the SAME pinned Sattolo operator (seed 20260712);
        # disclosed instantiation — the spec pins σ₂ over Swept only and §5 uses
        # Swept only, so this affects nothing gate-bearing.
        if not partial:
            cperm = _bp_sattolo(len(c100), BPRIME2_SEED)
            assert all(cperm[k] != k for k in range(len(c100))), "ABORT: C100 derangement fixed point"
            sigma_c100 = {c100[k]: c100[cperm[k]] for k in range(len(c100))}
            _run_disc(c100, cells, per_cell_c100, "disc-c100", False, sigma_c100)

        # ============ STEP 7a keyed-gen secondaries (pivot, Swept) ==============
        keyed = {"real": {"top": 0, "bridge": 0, "other": 0, "none": 0},
                 "drg": {"top": 0, "bridge": 0, "other": 0, "none": 0},
                 "rescue_real_plus": 0, "rescue_drg_plus": 0, "n": len(swept)}
        if not partial:
            for arm, vecfn in (("real", lambda i: dhat[i][plh]),
                               ("drg", lambda i: dhat[sigma[i]][plh])):
                for sgn in (1, -1):
                    for mb in _mini(swept):
                        idl = [prompt_ids[i] for i in mb]
                        vecs = [alpha_star * sgn * vecfn(i) for i in mb]
                        gens = _gen_add(idl, plt, vecs)
                        for i, g in zip(mb, gens):
                            s = specs[i]
                            cat = _emit_cat(g, s)
                            ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                            if sgn == 1:
                                keyed[arm][cat] += 1
                                if ok:
                                    keyed["rescue_%s_plus" % arm] += 1
                            rows.append(_row(item_id=s["item_id"], probe="keyed-gen",
                                             cell=[plh, plt], arm=arm, sign=sgn,
                                             alpha=alpha_star, coin=None, lp_top=None,
                                             lp_bridge=None, gen=g, correct=ok,
                                             emitted=cat, gold=s["gold_top"]))
            print("[bp2] keyed-gen done t=%.0fs" % (time.time() - t0))
        secondaries["keyed_emission"] = keyed

        # ============ STEP 7b breakage secondaries (C100, all cells) ============
        breakage_cell = {}
        collapse_cell = {}
        if not partial:
            for (lh, lt) in cells:
                bcnt = 0
                ccnt = 0
                for sgn in (1, -1):
                    for mb in _mini(c100):
                        idl = [prompt_ids[i] for i in mb]
                        vecs = [alpha_star * sgn * dhat[i][lh] for i in mb]
                        gens = _gen_add(idl, lt, vecs)
                        for i, g in zip(mb, gens):
                            s = specs[i]
                            ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                            if not ok:
                                bcnt += 1
                            if not _has_any(g, s["surfaces"]):
                                ccnt += 1
                            rows.append(_row(item_id=s["item_id"], probe="breakage",
                                             cell=[lh, lt], arm="real", sign=sgn,
                                             alpha=alpha_star, coin=None, lp_top=None,
                                             lp_bridge=None, gen=g, correct=ok,
                                             emitted=None, gold=s["gold_top"]))
                breakage_cell["%d_%d" % (lh, lt)] = bcnt
                collapse_cell["%d_%d" % (lh, lt)] = ccnt
            print("[bp2] breakage done t=%.0fs" % (time.time() - t0))
        secondaries["breakage_c100"] = breakage_cell
        secondaries["collapse_c100"] = collapse_cell

    except _B2Abort as e:
        aborted = True
        abort_reason = str(e)
        print("[bp2] ABORT:", abort_reason)

    # effect-size summaries (mechanical; reported)
    def _mm(a):
        if not a:
            return {"mean": None, "median": None, "n": 0}
        srt = sorted(a)
        med = srt[len(srt) // 2] if len(srt) % 2 else 0.5 * (srt[len(srt) // 2 - 1] + srt[len(srt) // 2])
        return {"mean": sum(a) / len(a), "median": med, "n": len(a)}

    per_cell_metrics = {}
    for key, acc in per_cell.items():
        per_cell_metrics[key] = {
            "n": len(acc["real"]),
            "keyacc_real": (sum(acc["real"]) / len(acc["real"]) if acc["real"] else None),
            "keyacc_coin": (sum(acc["coin"]) / len(acc["coin"]) if acc["coin"] else None),
            "keyacc_role": (sum(acc["role"]) / len(acc["role"]) if acc["role"] else None),
            "ties": {"real": acc["real_ties"], "coin": acc["coin_ties"], "role": acc["role_ties"]},
            "mdiff_real": _mm(acc["mdiff_real"]),
            "mdiff_role": _mm(acc["mdiff_role"]),
            "mdiff_coin": _mm(acc["mdiff_coin"]),
        }
    summary.update({"baseline_margin": _mm(baseline_margins),
                    "per_cell_metrics": per_cell_metrics,
                    "aborted": bool(aborted), "abort_reason": abort_reason,
                    "partial": bool(partial), "partial_reason": partial_reason,
                    "elapsed_s": time.time() - t0})

    return {
        "aborted": bool(aborted), "abort_reason": abort_reason,
        "partial": bool(partial), "partial_reason": partial_reason,
        "rows": [json.loads(json.dumps(r, default=str)) for r in rows],
        "summary": json.loads(json.dumps(summary, default=str)),
        "swept_item_ids": [specs[i]["item_id"] for i in swept],
        "c100_item_ids": [specs[i]["item_id"] for i in c100],
        "per_cell": {k: {"real": v["real"], "coin": v["coin"], "role": v["role"],
                         "real_ties": v["real_ties"], "coin_ties": v["coin_ties"],
                         "role_ties": v["role_ties"]}
                     for k, v in per_cell.items()},
        "per_cell_c100": {k: {"real": v["real"], "coin": v["coin"], "role": v["role"]}
                          for k, v in per_cell_c100.items()},
        "cells": [list(c) for c in cells],
        "completed_cells": completed_cells,
        "secondaries": secondaries,
        "elapsed_s": time.time() - t0,
    }


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=21600)
def bprime2_a10g(model_id, specs, bprime_text_correct, batch_size, wall_cap_s):
    r = _bprime2_body(model_id, specs, bprime_text_correct, batch_size, wall_cap_s)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return r


def _bprime2_gate(res):
    """Mechanical §5 decision rule from returned per-cell success arrays. Computes
    Wilson bounds (PASS z=2.5427 LB / KILL z=1.6449 UB / control z=2.7730 LB) +
    paired exact-binomial sign tests, applies the ordered gate. Runner reports
    these numbers; interpretation is designer work."""
    aborted = bool(res.get("aborted", False))
    summary = res.get("summary", {})
    headroom_ok = bool(summary.get("headroom_ok", False))
    per_cell = res.get("per_cell", {})
    cells = res.get("cells", [])
    completed = [tuple(c) for c in res.get("completed_cells", [])]
    FLOOR = BPRIME2_FLOOR

    def _paired(real, ctrl):
        b = sum(1 for x, y in zip(real, ctrl) if x and not y)
        c = sum(1 for x, y in zip(real, ctrl) if (not x) and y)
        p = _bp_binom_sf_ge(b, b + c, 0.5)
        return {"b": b, "c": c, "n_discordant": b + c, "p_one_sided": p}

    cell_reports = []
    any_coin_invalid = False
    pass_cell = None
    role_cell = None
    for c in cells:
        key = "%d_%d" % (c[0], c[1])
        pc = per_cell.get(key)
        if pc is None:
            continue
        rb, cb, ro = pc["real"], pc["coin"], pc["role"]
        nn = len(rb)
        kr, kc, kro = sum(rb), sum(cb), sum(ro)
        lb_real = _bp_wilson(kr, nn, BPRIME2_Z_PASS)[0]
        ub_real = _bp_wilson(kr, nn, BPRIME2_Z_KILL)[1]
        lb_coin = _bp_wilson(kc, nn, BPRIME2_Z_CTRL)[0]
        pr_coin = _paired(rb, cb)
        pr_role = _paired(rb, ro)
        is_done = tuple(c) in completed
        rep = {"cell": list(c), "n": nn, "completed": is_done,
               "keyacc_real": (kr / nn if nn else None),
               "keyacc_coin": (kc / nn if nn else None),
               "keyacc_role": (kro / nn if nn else None),
               "wilson_lb_real_z2_5427": lb_real, "wilson_ub95_real_z1_6449": ub_real,
               "wilson_lb_coin_z2_7730": lb_coin,
               "paired_real_gt_coin": pr_coin, "paired_real_gt_role": pr_role,
               "ties": {"real": pc["real_ties"], "coin": pc["coin_ties"], "role": pc["role_ties"]}}
        cell_reports.append(rep)
        if is_done and lb_coin > 0.5:
            any_coin_invalid = True
        if is_done and lb_real >= FLOOR and pr_coin["p_one_sided"] < 0.05 and pr_role["p_one_sided"] < 0.05 and pass_cell is None:
            pass_cell = list(c)
        if is_done and lb_real >= FLOOR and pr_coin["p_one_sided"] < 0.05 and role_cell is None:
            role_cell = list(c)

    all9_done = len(completed) == 9
    done_reports = [r for r in cell_reports if r["completed"]]
    all_kill = all9_done and len(done_reports) == 9 and all(r["wilson_ub95_real_z1_6449"] < FLOOR for r in done_reports)

    if aborted or (not headroom_ok) or any_coin_invalid:
        label = "INSTRUMENT-INVALID"
    elif pass_cell is not None:
        label = "PASS-KEYED"
    elif role_cell is not None:
        label = "CHANNEL-ROLE-ONLY"
    elif all_kill:
        label = "KILL-NO-USABLE-CHANNEL"
    else:
        label = "INCONCLUSIVE"

    return {
        "gate_label": label,
        "floor": FLOOR, "z": {"pass": BPRIME2_Z_PASS, "kill": BPRIME2_Z_KILL, "ctrl": BPRIME2_Z_CTRL},
        "headroom_ok": headroom_ok, "aborted": aborted,
        "partial": bool(res.get("partial", False)),
        "n_completed_cells": len(completed),
        "instrument_invalid_triggers": {
            "aborted": aborted, "not_headroom_ok": (not headroom_ok),
            "coin_lb_gt_0.5_any_cell": any_coin_invalid},
        "pass_cell": pass_cell, "role_only_cell": role_cell,
        "all9_kill": all_kill,
        "cell_reports": cell_reports,
        "alpha_star": summary.get("alpha_star"),
        "n_swept": summary.get("n_swept"),
    }


@app.local_entrypoint()
def bprime2(dry_plan: bool = False, gpu: str = "A10G"):
    import hashlib
    import time

    def _sha_file(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    # ---- input pins (spec §2 DECISION), ABORT on drift ----
    items_sha = _sha_file(_ROOT / "data/nsk1-clutrr/items.jsonl")
    head_sha = _sha_file(_ROOT / "data/nsk1-clutrr/headroom.jsonl")
    ITEMS_PIN = "0e1f5c6bad6f97b575e3c354803713c3efef2a25cf76a9745e79b3d584f5839e"
    HEAD_PIN = "8b8e99e48cce5fd40a8b7e858b4b75730c9a2d66e9237034f0d3b3b4468c4d8d"
    assert items_sha == ITEMS_PIN, "ABORT: items.jsonl sha mismatch %s" % items_sha
    assert head_sha == HEAD_PIN, "ABORT: headroom.jsonl sha mismatch %s" % head_sha

    specs = _build_specs_bprime2()
    n = len(specs)
    # byte-equality ASSERT: headroom-100 form-2 prompts == _build_specs_g2b f2_to
    g2b_specs, _vocab = _build_specs_g2b()
    g2b_f2 = {s["item_id"]: s["f2_to"] for s in g2b_specs}
    mine = {s["item_id"]: s["prompt"] for s in specs}
    mism = [iid for iid in g2b_f2 if g2b_f2[iid] != mine.get(iid)]
    assert not mism, "ABORT: form-2 prompt not byte-equal to g2b for %s" % mism[:5]
    print("[bp2] byte-equality vs _build_specs_g2b f2_to: 100/100 OK")

    # ---- B′ text-only correctness vector for the repro gate (spec §3 Step 1) ----
    bp_rows = _ROOT / "poc/nsk1/out/bprime/bprime_rows.jsonl"
    bprime_text_correct = {}
    for l in bp_rows.read_text().splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get("probe") == "text-only":
            bprime_text_correct[r["item_id"]] = bool(r["correct"])
    assert len(bprime_text_correct) >= 900, \
        "ABORT: B′ text-only reference incomplete (%d)" % len(bprime_text_correct)

    L_expected = 24
    LH, LT, pivot, cells = _bprime2_grid(L_expected)
    swept_plan = 200   # B′ measured |F| (spec §3 planning value)
    swept_worst = 300

    def _counts(nsw):
        gens = n + (len(BPRIME2_ALPHA_LADDER) * BPRIME2_CCAL * 2) + (nsw * 2 * 2) + (BPRIME2_C100 * len(cells) * 2)
        fwd_donor = 2 * (nsw + BPRIME2_C100)
        fwd_disc = nsw * len(cells) * 4 * 2
        fwd_c100 = BPRIME2_C100 * len(cells) * 4 * 2
        fwd_base = (nsw + BPRIME2_C100) * 2
        fwd = fwd_donor + fwd_disc + fwd_c100 + fwd_base
        return gens, fwd, (fwd_donor, fwd_disc, fwd_c100, fwd_base)

    gens_p, fwd_p, brk_p = _counts(swept_plan)
    gens_w, fwd_w, brk_w = _counts(swept_worst)
    # GPU-h / $ planning band = spec §7 (STIPULATED-grade planning, not a measurement)
    gpuh_lo, gpuh_hi = 0.3, 1.5
    usd_lo, usd_hi = 0.4, 2.0

    print("=== B″ Stage-0 KEYED internal-channel probe — PLAN (spec docs/next/nsk1-bprime2-spec.md) ===")
    print("host                : R3 = %s  commit-pin %s" % (BPRIME2_MODEL, BPRIME2_PIN))
    print("items (covered)     : %d (858 items.jsonl covered + 100 headroom.jsonl)" % n)
    print("input pins OK       : items=%s… headroom=%s…" % (items_sha[:12], head_sha[:12]))
    print("grid (L=%d)          : LH=%s LT=%s  pivot=%s  |cells|=%d" % (L_expected, LH, LT, pivot, len(cells)))
    print("cell sweep order    : %s" % cells)
    print("seeds               : %d (σ₂ / C100 / 300-cap / coin)" % BPRIME2_SEED)
    print("α ladder            : %s  (α*=largest with name-collapse≤0.10 at pivot; else 0.125)" % BPRIME2_ALPHA_LADDER)
    print("floor / z           : %.2f  |  PASS-LB z=%.4f  KILL-UB z=%.4f  CTRL z=%.4f" % (BPRIME2_FLOOR, BPRIME2_Z_PASS, BPRIME2_Z_KILL, BPRIME2_Z_CTRL))
    print("planning |Swept|    : %d (=B′ measured |F|; actual = text-only failures, cap %d)" % (swept_plan, BPRIME2_SWEEP_CAP))
    print("gens   @|Swept|=%d  : %d  (text-only %d + calib %d + keyed %d + breakage %d)"
          % (swept_plan, gens_p, n, len(BPRIME2_ALPHA_LADDER) * BPRIME2_CCAL * 2, swept_plan * 4, BPRIME2_C100 * len(cells) * 2))
    print("forwards@|Swept|=%d : %d  (donor %d + disc %d + disc-c100 %d + baseline %d)"
          % (swept_plan, fwd_p, brk_p[0], brk_p[1], brk_p[2], brk_p[3]))
    print("worst  @|Swept|=%d  : gens=%d forwards=%d" % (swept_worst, gens_w, fwd_w))
    print("GPU-h estimate      : %.1f–%.1f  |  $ estimate : $%.1f–$%.1f  (A10G fp32; spec §7 planning band)" % (gpuh_lo, gpuh_hi, usd_lo, usd_hi))
    print("HARD caps           : $25 / 10 GPU-h / 12 h wall  (in-container soft wall guard %ds)" % BPRIME2_WALL_CAP_S)
    print("decision rule       : §5 — INSTRUMENT-INVALID → PASS-KEYED → CHANNEL-ROLE-ONLY → KILL → INCONCLUSIVE (ties=failure)")
    print("phase               : exploratory (quarantined, uncitable, flips no verdict)")

    caps_ok = (gpuh_hi <= 10 and usd_hi <= 25 and gens_w + fwd_w <= 120000)
    print("within caps (plan)  : %s" % caps_ok)

    if dry_plan:
        s0 = specs[0]
        print("\nDRY-PLAN ONLY — no GPU launched, $0 spent. All build asserts passed.")
        print("\n--- sample form-2 text-only prompt (item %s) ---\n%s" % (s0["item_id"], s0["prompt"]))
        print("\n--- donors (item %s) ---\nD_top   : %s\nD_bridge: %s\n[top=%s bridge=%s base=%s]"
              % (s0["item_id"], s0["d_top"], s0["d_bridge"], s0["top_surface"], s0["bridge_surface"], s0["base"]))
        print("\ncoin-bit sample (item %s, pivot %s): b=%d"
              % (s0["item_id"], pivot, _bprime2_coin_bit(s0["item_id"], pivot[0], pivot[1])))
        return

    if not caps_ok:
        raise SystemExit("ABORT: plan exceeds caps — not launching")

    t_launch = time.time()
    res = bprime2_a10g.remote(BPRIME2_MODEL, specs, bprime_text_correct,
                              BPRIME2_BATCH, BPRIME2_WALL_CAP_S)
    wall_s = time.time() - t_launch

    outdir = _ROOT / "poc/nsk1/out/bprime2"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = res.get("rows", [])
    with open(outdir / "bprime2_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    gate = _bprime2_gate(res)
    summary = dict(res.get("summary", {}))
    elapsed = res.get("summary", {}).get("elapsed_s", res.get("elapsed_s", 0.0)) or 0.0
    summary.update({
        "spec_ref": "docs/next/nsk1-bprime2-spec.md",
        "gate": "BPRIME2", "phase": "exploratory",
        "input_pins": {"items_jsonl_sha256": items_sha, "headroom_jsonl_sha256": head_sha},
        "verdict": gate, "secondaries": res.get("secondaries", {}),
        "swept_item_ids": res.get("swept_item_ids", []),
        "c100_item_ids": res.get("c100_item_ids", []),
        "wall_clock_s_local": round(wall_s, 1),
        "gpu_h_estimate": round(elapsed / 3600.0, 3),
        "usd_estimate": round(elapsed / 3600.0 * 1.10, 3),
        "n_rows": len(rows),
        "aborted": bool(res.get("aborted", False)), "abort_reason": res.get("abort_reason"),
        "partial": bool(res.get("partial", False)), "partial_reason": res.get("partial_reason"),
        "hard_caps": {"usd": 25, "gpu_h": 10, "wall_h": 12},
    })
    with open(outdir / "bprime2_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    sha_rows = _sha_file(outdir / "bprime2_rows.jsonl")
    sha_sum = _sha_file(outdir / "bprime2_summary.json")
    print("\n=== B″ RESULT (phase:exploratory) ===")
    print("aborted=%s partial=%s n_rows=%d elapsed=%.0fs (GPU) / %.0fs (wall)"
          % (res.get("aborted"), res.get("partial"), len(rows), elapsed, wall_s))
    print(json.dumps(gate, indent=1, sort_keys=True))
    print("MECHANICAL VERDICT (spec §5): %s" % gate["gate_label"])
    print("sha256 bprime2_rows.jsonl    = %s" % sha_rows)
    print("sha256 bprime2_summary.json  = %s" % sha_sum)


# =====================================================================
# nsk1 STAGE-1 — free-generation KEYED-RESCUE probe at R3, phase:"exploratory"
# ---------------------------------------------------------------------
# EXECUTES docs/next/nsk1-stage1-spec.md (Fable, runner-ready; ASM-0400..0404;
# ZERO design decisions left to the runner). Successor to B″ (bprime2). This
# entrypoint is APPENDED; the g2/g2b/g2c/g2d/bprime/bprime2 code and every shared
# helper above are byte-untouched. It REUSES the verified B″ instrument:
#   * specs = _build_specs_bprime2() VERBATIM (958 form-2 prompts + D_top/D_bridge
#     donors + all build asserts + byte-equality vs _build_specs_g2b f2_to).
#   * _score_entity scorer byte-verbatim; _bp_wilson / _bp_binom_sf_ge /
#     _bp_sattolo / _bprime2_coin_bit / _B2Abort byte-verbatim.
#   * the B″ additive norm-matched pre-hook (h_p ← h_p + s·α·‖h_p‖·Δ̂v at the
#     final prompt-token position, prefill only) re-created here identically.
# NEW read-out (spec §1/§2): moves from teacher-forced margins to FREE GENERATION
#   at the 2 measured keying cells [(12,16),(16,16)] (ASSERT L=24), over the α
#   ladder {0.25,0.5,0.75,1.0} (α-descending, 1.0 anchor first), scoring keyed
#   emission + RESCUE of text-only failures. Two pre-fixed endpoints (ASM-0404):
#   R− (integration rescue, real −, echo-proof) and R+ (delivered-conclusion
#   rescue, real +, echo-confounded). Content-specificity via 3 independent
#   Sattolo derangements (seeds 20260712/13/14) with the coin (content-free null)
#   and role (role-consistent) controls DERIVED from the same deranged gens.
# Host R3 = SmolLM2-1.7B-Instruct, commit-pinned; A10G fp32; all 958 covered
# CLUTRR entity-form items; greedy 16-tok gens; every row phase:"exploratory".
#
#   poc/modal/.venv/bin/modal run poc/modal/modal_nsk1_g2.py::stage1 --dry-plan   # $0
#   poc/modal/.venv/bin/modal run poc/modal/modal_nsk1_g2.py::stage1              # A10G
# =====================================================================

STAGE1_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"           # R3 (ASM-0040/0400)
STAGE1_PIN = "31b70e2e869a7173562077fd711b654946d38674"         # commit pin (ABORT otherwise)
STAGE1_CELLS = [(12, 16), (16, 16)]                             # the 2 measured keying cells (ASM-0400)
STAGE1_HARVEST_LH = sorted({c[0] for c in STAGE1_CELLS})        # donor-harvest layers = [12, 16]
STAGE1_ALPHA_LADDER = [1.0, 0.75, 0.5, 0.25]                    # α-DESCENDING, 1.0 anchor first (spec §3 Step 6)
STAGE1_SEEDS = [20260712, 20260713, 20260714]                   # σ_a / σ_b / σ_c derangement seeds (ASM-0400)
STAGE1_SAMPLE_SEED = 20260712                                   # Swept 300-sample + C100 sample (ASM-0400)
STAGE1_SWEEP_CAP = 300                                          # Swept cap (spec §2)
STAGE1_C100 = 100                                               # correct subsample size (spec §2)
STAGE1_BATCH = 16                                               # GPU mini-batch (OOM auto-halves)
STAGE1_WALL_CAP_S = 19800                                       # soft in-container wall guard (5.5 h)
STAGE1_REPL_FLOOR = 0.70                                        # B″ keying-replication floor (spec §2/§5)
STAGE1_Z_KILL = 1.6449                                          # one-sided 95% (Wilson UB / pooled UB), Φ⁻¹(0.95)
STAGE1_Z_CTRL = 3.2790                                          # control-validity tripwire (two-sided 0.05 / 48 series×2 sides)
STAGE1_P_COIN = 0.05 / 8                                        # per-endpoint Bonferroni over 8 (cell×α) combos = 0.00625
STAGE1_P_ROLE = 0.05                                            # role-conjunct threshold (spec §5)
STAGE1_DELTA_MEAN_FLOOR = 0.10                                  # mean_s Δ_es floor (spec §5)
STAGE1_DELTA_MIN_FLOOR = 0.05                                   # min_s Δ_es floor (spec §5)
STAGE1_KILL_UB = 0.10                                           # pooled-UB KILL margin (spec §5)
# input pins reused from B″ (spec §2: "same input-pin sha256s as B″ §2, ABORT on drift")
STAGE1_ITEMS_PIN = "0e1f5c6bad6f97b575e3c354803713c3efef2a25cf76a9745e79b3d584f5839e"
STAGE1_HEAD_PIN = "8b8e99e48cce5fd40a8b7e858b4b75730c9a2d66e9237034f0d3b3b4468c4d8d"


# ----------------------------------------------------- GPU body (torch, remote)
def _stage1_body(model_id, specs, bprime2_text_correct, batch_size, wall_cap_s):
    import traceback
    try:
        return _stage1_body_impl(model_id, specs, bprime2_text_correct,
                                 batch_size, wall_cap_s)
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        print("STAGE1 ERROR:", repr(e))
        print(tb)
        return {"aborted": True, "abort_reason": "EXCEPTION: %s" % repr(e),
                "traceback": tb, "rows": [], "summary": {}, "swept_item_ids": [],
                "c100_item_ids": [], "per_unit": {}, "completed_units": []}


def _stage1_body_impl(model_id, specs, bprime2_text_correct, batch_size, wall_cap_s):
    import re
    import time
    import math
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    n = len(specs)
    tok = AutoTokenizer.from_pretrained(model_id, revision=STAGE1_PIN)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, revision=STAGE1_PIN, torch_dtype=torch.float32)
    model.to("cuda").eval()
    L = int(model.config.num_hidden_layers)
    d_model = int(model.config.hidden_size)
    commit = getattr(model.config, "_commit_hash", None)

    def _abort_ret(reason, summ=None):
        return {"aborted": True, "abort_reason": reason, "rows": [],
                "summary": (summ or {"model_commit": commit}),
                "swept_item_ids": [], "c100_item_ids": [], "per_unit": {},
                "completed_units": []}

    # spec §2: resolved commit MUST equal the pin (ABORT otherwise)
    if commit is not None and commit != STAGE1_PIN:
        return _abort_ret("COMMIT_PIN_MISMATCH got=%s want=%s" % (commit, STAGE1_PIN))
    # spec §3 Step 2: ASSERT L == 24
    if L != 24:
        return _abort_ret("L_NOT_24 got=%d" % L)
    layers = model.model.layers
    print("[s1] model=%s L=%d d=%d commit=%s" % (model_id, L, d_model, commit))
    print("[s1] cells=%s harvest_lh=%s alpha_ladder=%s seeds=%s"
          % (STAGE1_CELLS, STAGE1_HARVEST_LH, STAGE1_ALPHA_LADDER, STAGE1_SEEDS))

    # ---- additive norm-matched pre-hook (edits INPUT of module ℓt at pos w) ----
    # byte-mirror of B″'s add_pre_hook (spec §2: injection operator UNCHANGED).
    hook_state = {"vec": None, "wpos": None}  # vec=[bs,d]=s·α·Δ̂v ; wpos=[bs] long

    def add_pre_hook(module, args, kwargs):
        st = hook_state
        if st["vec"] is None:
            return None
        hs = None
        where = None
        if len(args) > 0 and torch.is_tensor(args[0]) and args[0].dim() == 3:
            hs, where = args[0], "arg"
        elif torch.is_tensor(kwargs.get("hidden_states")):
            hs, where = kwargs["hidden_states"], "kw"
        if hs is None or hs.shape[1] <= 1:
            return None  # decode step (seq==1): prefill-only (spec §2/§3)
        hs = hs.clone()
        u = st["vec"].to(hs.dtype)              # [bs, d]
        wpos = st["wpos"]                        # [bs] long
        bs = hs.shape[0]
        rws = torch.arange(bs, device=hs.device)
        cur = hs[rws, wpos, :]                    # [bs, d]
        nrm = cur.norm(dim=-1, keepdim=True)      # [bs, 1] = ‖h_p‖
        hs[rws, wpos, :] = cur + nrm * u          # h ← h + ‖h‖·(s·α·Δ̂v)
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

    def _mini(items):
        for a in range(0, len(items), batch_size):
            yield items[a:a + batch_size]

    def _gen_plain(id_lists):
        try:
            ii, am, maxlen = _pad_batch(id_lists)
            with torch.no_grad():
                out = model.generate(input_ids=ii, attention_mask=am,
                                     max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                                     num_beams=1, pad_token_id=tok.pad_token_id)
            return [tok.decode(out[r][maxlen:], skip_special_tokens=True)
                    for r in range(len(id_lists))]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(id_lists) == 1:
                raise
            h = len(id_lists) // 2
            return _gen_plain(id_lists[:h]) + _gen_plain(id_lists[h:])

    def _gen_add(id_lists, lt, vecs_signed):
        """Greedy 16-tok gen with the additive hook at layer lt, final prompt pos
        (prefill only). vecs_signed[r]=s·α·Δ̂v (unit dir). OOM->halve."""
        try:
            ii, am, maxlen = _pad_batch(id_lists)
            handle = None
            if lt is not None and vecs_signed is not None:
                hook_state["vec"] = torch.stack(vecs_signed).to("cuda")
                hook_state["wpos"] = torch.full((len(id_lists),), maxlen - 1,
                                                device="cuda", dtype=torch.long)
                handle = layers[lt].register_forward_pre_hook(add_pre_hook, with_kwargs=True)
            try:
                with torch.no_grad():
                    out = model.generate(input_ids=ii, attention_mask=am,
                                         max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                                         num_beams=1, pad_token_id=tok.pad_token_id)
            finally:
                if handle is not None:
                    handle.remove()
                hook_state["vec"] = None
                hook_state["wpos"] = None
            return [tok.decode(out[r][maxlen:], skip_special_tokens=True)
                    for r in range(len(id_lists))]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(id_lists) == 1:
                raise
            h = len(id_lists) // 2
            v1 = vecs_signed[:h] if vecs_signed is not None else None
            v2 = vecs_signed[h:] if vecs_signed is not None else None
            return _gen_add(id_lists[:h], lt, v1) + _gen_add(id_lists[h:], lt, v2)

    prompt_ids = [None] * n
    cand_ids = [None] * n  # per item: {'top': ids, 'bridge': ids}

    def _tf_lp(mb, cand_key, lt, vec_for):
        """Teacher-forced Σ logprob of candidate cand_key for each item idx in mb,
        under additive injection at layer lt (vec_for(i)=s·α·Δ̂v_i) at the last
        prompt-token position w=maxlen−len(cand)−1. lt/vec_for None => unhooked
        baseline. ASSERTs write-index; OOM->halve. (byte-mirror of B″ _tf_lp)"""
        try:
            id_lists = [prompt_ids[i] + cand_ids[i][cand_key] for i in mb]
            clens = [len(cand_ids[i][cand_key]) for i in mb]
            ii, am, maxlen = _pad_batch(id_lists)
            wrows = [maxlen - clens[r] - 1 for r in range(len(mb))]
            for r, i in enumerate(mb):
                if int(ii[r, wrows[r]].item()) != prompt_ids[i][-1]:
                    raise _B2Abort("WRITE_INDEX_MISMATCH item=%s" % specs[i]["item_id"])
            handle = None
            if lt is not None and vec_for is not None:
                u = torch.stack([vec_for(i) for i in mb]).to("cuda")
                hook_state["vec"] = u
                hook_state["wpos"] = torch.tensor(wrows, device="cuda", dtype=torch.long)
                handle = layers[lt].register_forward_pre_hook(add_pre_hook, with_kwargs=True)
            try:
                with torch.no_grad():
                    out = model(input_ids=ii, attention_mask=am)
            finally:
                if handle is not None:
                    handle.remove()
                hook_state["vec"] = None
                hook_state["wpos"] = None
            logits = out.logits
            lps = []
            for r, i in enumerate(mb):
                w = wrows[r]
                cid = cand_ids[i][cand_key]
                lp = 0.0
                for j, tid in enumerate(cid):
                    lr = torch.log_softmax(logits[r, w + j, :].float(), dim=-1)
                    lp += float(lr[tid].item())
                lps.append(lp)
            del out, logits
            return lps
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(mb) == 1:
                raise
            h = len(mb) // 2
            return _tf_lp(mb[:h], cand_key, lt, vec_for) + _tf_lp(mb[h:], cand_key, lt, vec_for)

    def _has_any(g, surfaces):
        t = g.lower()
        return any(re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(x.lower()), t)
                   for x in surfaces)

    def _emit_cat(g, s):
        t = g.lower()
        pos = {}
        for role, name in (("top", s["top_surface"]), ("bridge", s["bridge_surface"]),
                           ("base", s["base"])):
            mt = re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(name.lower()), t)
            if mt:
                pos[role] = mt.start()
        if not pos:
            return "none"
        first = min(pos, key=pos.get)
        return {"top": "top", "bridge": "bridge", "base": "other"}[first]

    def _mm(a):
        if not a:
            return {"mean": None, "median": None, "n": 0}
        srt = sorted(a)
        med = srt[len(srt) // 2] if len(srt) % 2 else 0.5 * (srt[len(srt) // 2 - 1] + srt[len(srt) // 2])
        return {"mean": sum(a) / len(a), "median": med, "n": len(a)}

    def _row(**kw):
        base = {"phase": "exploratory", "gate": "NSK1-S1", "host": "R3",
                "model": model_id, "surface": "clutrr", "form": "2",
                "item_id": None, "probe": None, "arm": None, "sign": None,
                "cell": None, "alpha": None, "seed": None, "coin": None,
                "lp_top": None, "lp_bridge": None, "gen": None, "correct": None,
                "emitted": None, "gold": None}
        base.update(kw)
        return base

    rows = []

    # =============== STEP 1: text-only pass (958 batched gens) ===================
    for i, s in enumerate(specs):
        prompt_ids[i] = _chat_ids(s["prompt"])
    text_only = [False] * n
    text_gen = [None] * n
    done = 0
    for mb in _mini(list(range(n))):
        gens = _gen_plain([prompt_ids[i] for i in mb])
        for i, g in zip(mb, gens):
            s = specs[i]
            ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
            text_only[i] = ok
            text_gen[i] = g
        done += len(mb)
        if done % 160 == 0 or done == n:
            print("[s1] step1 %d/%d acc_running=%.3f t=%.0fs"
                  % (done, n, sum(text_only[:done]) / max(1, done), time.time() - t0))
    acc_text = sum(text_only) / n
    headroom_ok = (0.05 <= acc_text <= 0.85) and (n >= 900)
    # repro gate vs B″ text-only correctness vector (spec §3 Step 1); <910/958 => ABORT
    repro_agree = 0
    repro_disagree = []
    for i, s in enumerate(specs):
        ref = bprime2_text_correct.get(s["item_id"])
        if ref is not None and bool(text_only[i]) == bool(ref):
            repro_agree += 1
        elif ref is not None:
            repro_disagree.append(s["item_id"])
    print("[s1] STEP1 acc_text=%.4f headroom_ok=%s repro_agree=%d/958"
          % (acc_text, headroom_ok, repro_agree))
    for i, s in enumerate(specs):
        rows.append(_row(item_id=s["item_id"], probe="text-only", gen=text_gen[i],
                         correct=bool(text_only[i]), gold=s["gold_top"]))

    summary = {
        "model": model_id, "model_commit": commit, "L": L, "d_model": d_model,
        "cells": [list(c) for c in STAGE1_CELLS], "harvest_lh": STAGE1_HARVEST_LH,
        "alpha_ladder": STAGE1_ALPHA_LADDER, "seeds": STAGE1_SEEDS,
        "sample_seed": STAGE1_SAMPLE_SEED,
        "coin_bit_recipe": "int(sha256('seed|item_id|lh|lt').hexdigest(),16)&1 (derangement seed in seed slot, alpha-independent)",
        "z": {"kill": STAGE1_Z_KILL, "ctrl": STAGE1_Z_CTRL},
        "p_coin_bonferroni": STAGE1_P_COIN, "p_role": STAGE1_P_ROLE,
        "delta_mean_floor": STAGE1_DELTA_MEAN_FLOOR, "delta_min_floor": STAGE1_DELTA_MIN_FLOOR,
        "kill_ub": STAGE1_KILL_UB, "repl_floor": STAGE1_REPL_FLOOR,
        "n_items": n, "n_scored": n, "acc_text_only": acc_text,
        "headroom_ok": bool(headroom_ok), "repro_agree": repro_agree,
        "repro_disagreements": repro_disagree, "batch_size": batch_size,
    }

    def _early(reason):
        summary.update({"aborted": True, "abort_reason": reason,
                        "elapsed_s": time.time() - t0})
        return {"aborted": True, "abort_reason": reason, "rows": rows,
                "summary": summary, "swept_item_ids": [], "c100_item_ids": [],
                "per_unit": {}, "completed_units": []}

    if repro_agree < 910:
        return _early("REPRO_DRIFT repro_agree=%d<910" % repro_agree)
    if not headroom_ok:
        return _early("HEADROOM acc_text=%.4f n=%d" % (acc_text, n))

    # =============== STEP 3: sets, derangements, coins ==========================
    F = [i for i in range(n) if not text_only[i]]
    correct_idx = [i for i in range(n) if text_only[i]]
    if len(F) <= STAGE1_SWEEP_CAP:
        swept = list(F)
    else:
        swept = sorted(_bp_random.Random(STAGE1_SAMPLE_SEED).sample(F, STAGE1_SWEEP_CAP))
    if len(correct_idx) < STAGE1_C100:
        return _early("C100_SHORT only %d correct (<%d)" % (len(correct_idx), STAGE1_C100))
    c100 = sorted(_bp_random.Random(STAGE1_SAMPLE_SEED).sample(correct_idx, STAGE1_C100))
    assert not (set(swept) & set(c100)), "ABORT: Swept∩C100 nonempty"
    assert len(c100) == STAGE1_C100, "ABORT: |C100|=%d != %d" % (len(c100), STAGE1_C100)
    m = len(swept)
    # three independent Sattolo derangements over Swept ascending order (ASM-0400)
    perms = {}
    sigma_by_seed = {}
    for si in STAGE1_SEEDS:
        p = _bp_sattolo(m, si)
        assert all(p[k] != k for k in range(m)), "ABORT: σ seed=%d has fixed point" % si
        perms[si] = p
        sigma_by_seed[si] = {swept[k]: swept[p[k]] for k in range(m)}
    # pairwise σ agreement counts (report-only): positions mapping to same target
    sigma_agreement = {}
    for a_i in range(len(STAGE1_SEEDS)):
        for b_i in range(a_i + 1, len(STAGE1_SEEDS)):
            sa, sb = STAGE1_SEEDS[a_i], STAGE1_SEEDS[b_i]
            sigma_agreement["%d_%d" % (sa, sb)] = sum(
                1 for k in range(m) if perms[sa][k] == perms[sb][k])
    print("[s1] |F|=%d |Swept|=%d |C100|=%d (3 σ fixed-point-free) σ_agree=%s"
          % (len(F), m, len(c100), sigma_agreement))
    summary.update({"n_failures": len(F), "n_swept": m, "n_c100": len(c100),
                    "swept_is_full_F": len(F) <= STAGE1_SWEEP_CAP,
                    "sigma_pairwise_agreement": sigma_agreement})

    # candidate token ids (spec §2 host UNCHANGED; B″ recipe)
    need = sorted(set(swept) | set(c100))
    for i in need:
        s = specs[i]
        for key, name in (("top", s["top_surface"]), ("bridge", s["bridge_surface"])):
            cid = tok(" " + name, add_special_tokens=False).input_ids
            assert len(cid) >= 1, "ABORT: empty cand ids (%s)" % s["item_id"]
            if cand_ids[i] is None:
                cand_ids[i] = {}
            cand_ids[i][key] = list(cid)

    aborted = False
    abort_reason = None
    partial = False
    partial_reason = None
    completed_units = []
    per_unit = {}
    baseline_margins = []
    dhat = {}

    try:
        # ============ STEP 4: donor harvest (Δ̂v at ℓh ∈ {12,16}) ================
        def _last_name_tok(text, name, offsets):
            cstart = text.rfind(name)
            if cstart < 0:
                return None
            cend = cstart + len(name)
            found = None
            for ti, (a, b) in enumerate(offsets):
                if a == b:
                    continue
                if a < cend and b > cstart:
                    found = ti
            return found

        for i in need:
            s = specs[i]
            hv = {}
            for key, name, text in (("top", s["top_surface"], s["d_top"]),
                                    ("bridge", s["bridge_surface"], s["d_bridge"])):
                enc = tok(text, return_offsets_mapping=True)
                ti = _last_name_tok(text, name, enc["offset_mapping"])
                if ti is None:
                    raise _B2Abort("NAME_LOCATION donor=%s item=%s" % (key, s["item_id"]))
                idt = torch.tensor([enc["input_ids"]], device="cuda")
                with torch.no_grad():
                    fwd = model(idt, output_hidden_states=True)
                hv[key] = {lh: fwd.hidden_states[lh][0, ti, :].detach().float().clone()
                           for lh in STAGE1_HARVEST_LH}
                del fwd
            dv = {}
            for lh in STAGE1_HARVEST_LH:
                d = hv["top"][lh] - hv["bridge"][lh]
                if not (float(d.norm()) > 0):
                    raise _B2Abort("DELTA_ZERO item=%s lh=%d" % (s["item_id"], lh))
                dv[lh] = d / d.norm()
            dhat[i] = dv
        print("[s1] donors harvested for %d items (no gen) t=%.0fs"
              % (len(need), time.time() - t0))

        # ============ STEP 5: unhooked baselines (Swept ∪ C100) =================
        for mb in _mini(need):
            lpt = _tf_lp(mb, "top", None, None)
            lpb = _tf_lp(mb, "bridge", None, None)
            for r_idx, i in enumerate(mb):
                s = specs[i]
                if not (math.isfinite(lpt[r_idx]) and math.isfinite(lpb[r_idx])):
                    raise _B2Abort("NAN_BASELINE item=%s" % s["item_id"])
                baseline_margins.append(lpt[r_idx] - lpb[r_idx])
                rows.append(_row(item_id=s["item_id"], probe="baseline",
                                 lp_top=lpt[r_idx], lp_bridge=lpb[r_idx],
                                 gold=s["gold_top"]))
        print("[s1] baselines done t=%.0fs" % (time.time() - t0))

        # ============ STEP 6: per-α tiers (α DESCENDING; cells in order) =========
        skeys = [str(si) for si in STAGE1_SEEDS]
        for alpha in STAGE1_ALPHA_LADDER:
            if partial:
                break
            for (lh, lt) in STAGE1_CELLS:
                # wall-guard check BETWEEN (α, cell) units (spec §3 Step 6)
                if time.time() - t0 > wall_cap_s:
                    partial, partial_reason = True, "WALL_CAP before unit alpha=%g cell=%d_%d" % (alpha, lh, lt)
                    break
                ukey = "%g|%d_%d" % (alpha, lh, lt)

                # -------- (6a) margin sweep (Swept) --------
                m_acc = {"real": [], "coin": {sk: [] for sk in skeys},
                         "role": {sk: [] for sk in skeys},
                         "real_ties": 0, "coin_ties": {sk: 0 for sk in skeys},
                         "role_ties": {sk: 0 for sk in skeys},
                         "mdiff_real": [], "mdiff_role": {sk: [] for sk in skeys},
                         "mdiff_coin": {sk: [] for sk in skeys}}
                for mb in _mini(swept):
                    def _mgn(vecfn):
                        r = {}
                        for sgn in (1, -1):
                            vf = (lambda i, sgn=sgn, vecfn=vecfn:
                                  alpha * sgn * vecfn(i))
                            lpt = _tf_lp(mb, "top", lt, vf)
                            lpb = _tf_lp(mb, "bridge", lt, vf)
                            r[sgn] = (lpt, lpb)
                        return r
                    real = _mgn(lambda i: dhat[i][lh])
                    drg = {si: _mgn(lambda i, si=si: dhat[sigma_by_seed[si][i]][lh])
                           for si in STAGE1_SEEDS}
                    for r_idx, i in enumerate(mb):
                        s = specs[i]
                        rp_t, rp_b = real[1][0][r_idx], real[1][1][r_idx]
                        rm_t, rm_b = real[-1][0][r_idx], real[-1][1][r_idx]
                        dvals = {}
                        allvals = [rp_t, rp_b, rm_t, rm_b]
                        for si in STAGE1_SEEDS:
                            dp_t, dp_b = drg[si][1][0][r_idx], drg[si][1][1][r_idx]
                            dm_t, dm_b = drg[si][-1][0][r_idx], drg[si][-1][1][r_idx]
                            dvals[si] = (dp_t, dp_b, dm_t, dm_b)
                            allvals += [dp_t, dp_b, dm_t, dm_b]
                        if not all(math.isfinite(v) for v in allvals):
                            raise _B2Abort("NAN_MARGINS item=%s cell=%d_%d alpha=%g"
                                           % (s["item_id"], lh, lt, alpha))
                        mr_p = rp_t - rp_b
                        mr_m = rm_t - rm_b
                        real_bit = 1 if mr_p > mr_m else 0
                        m_acc["real"].append(real_bit)
                        if mr_p == mr_m:
                            m_acc["real_ties"] += 1
                        m_acc["mdiff_real"].append(mr_p - mr_m)
                        rows.append(_row(item_id=s["item_id"], probe="margin", cell=[lh, lt],
                                         arm="real", sign=1, alpha=alpha, lp_top=rp_t,
                                         lp_bridge=rp_b, gold=s["gold_top"]))
                        rows.append(_row(item_id=s["item_id"], probe="margin", cell=[lh, lt],
                                         arm="real", sign=-1, alpha=alpha, lp_top=rm_t,
                                         lp_bridge=rm_b, gold=s["gold_top"]))
                        for si in STAGE1_SEEDS:
                            sk = str(si)
                            dp_t, dp_b, dm_t, dm_b = dvals[si]
                            md_p = dp_t - dp_b
                            md_m = dm_t - dm_b
                            b = _bprime2_coin_bit(s["item_id"], lh, lt, seed=si)
                            role_bit = 1 if md_p > md_m else 0
                            coin_bit = (1 if md_p > md_m else 0) if b == 1 else (1 if md_m > md_p else 0)
                            m_acc["role"][sk].append(role_bit)
                            m_acc["coin"][sk].append(coin_bit)
                            if md_p == md_m:
                                m_acc["role_ties"][sk] += 1
                                m_acc["coin_ties"][sk] += 1
                            m_acc["mdiff_role"][sk].append(md_p - md_m)
                            m_acc["mdiff_coin"][sk].append((md_p - md_m) if b == 1 else (md_m - md_p))
                            rows.append(_row(item_id=s["item_id"], probe="margin", cell=[lh, lt],
                                             arm="drg", sign=1, alpha=alpha, seed=si, coin=b,
                                             lp_top=dp_t, lp_bridge=dp_b, gold=s["gold_top"]))
                            rows.append(_row(item_id=s["item_id"], probe="margin", cell=[lh, lt],
                                             arm="drg", sign=-1, alpha=alpha, seed=si, coin=b,
                                             lp_top=dm_t, lp_bridge=dm_b, gold=s["gold_top"]))

                # -------- (6b) rescue generations (Swept) --------
                gen_real = {1: {}, -1: {}}
                gen_drg = {si: {1: {}, -1: {}} for si in STAGE1_SEEDS}
                for sgn in (1, -1):
                    for mb in _mini(swept):
                        idl = [prompt_ids[i] for i in mb]
                        vecs = [alpha * sgn * dhat[i][lh] for i in mb]
                        gens = _gen_add(idl, lt, vecs)
                        for i, g in zip(mb, gens):
                            s = specs[i]
                            cat = _emit_cat(g, s)
                            ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                            gen_real[sgn][i] = (g, cat, ok)
                            rows.append(_row(item_id=s["item_id"], probe="rescue-gen",
                                             cell=[lh, lt], arm="real", sign=sgn, alpha=alpha,
                                             gen=g, correct=ok, emitted=cat, gold=s["gold_top"]))
                for si in STAGE1_SEEDS:
                    for sgn in (1, -1):
                        for mb in _mini(swept):
                            idl = [prompt_ids[i] for i in mb]
                            vecs = [alpha * sgn * dhat[sigma_by_seed[si][i]][lh] for i in mb]
                            gens = _gen_add(idl, lt, vecs)
                            for i, g in zip(mb, gens):
                                s = specs[i]
                                cat = _emit_cat(g, s)
                                ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                                b = _bprime2_coin_bit(s["item_id"], lh, lt, seed=si)
                                gen_drg[si][sgn][i] = (g, cat, ok)
                                rows.append(_row(item_id=s["item_id"], probe="rescue-gen",
                                                 cell=[lh, lt], arm="drg", sign=sgn, alpha=alpha,
                                                 seed=si, coin=b, gen=g, correct=ok,
                                                 emitted=cat, gold=s["gold_top"]))
                # derive per-item rescue/emission bits (spec §3 Step 6b / §4)
                r_acc = {"real_plus": [], "real_minus": [],
                         "coin": {sk: [] for sk in skeys},
                         "role_plus": {sk: [] for sk in skeys},
                         "role_minus": {sk: [] for sk in skeys},
                         "keyem_real": [], "keyem_role": {sk: [] for sk in skeys},
                         "keyem_coin": {sk: [] for sk in skeys}}
                for i in swept:
                    s = specs[i]
                    rp = gen_real[1][i]
                    rm = gen_real[-1][i]
                    r_acc["real_plus"].append(1 if rp[2] else 0)
                    r_acc["real_minus"].append(1 if rm[2] else 0)
                    r_acc["keyem_real"].append(1 if (rp[1] == "top" and rm[1] == "bridge") else 0)
                    for si in STAGE1_SEEDS:
                        sk = str(si)
                        b = _bprime2_coin_bit(s["item_id"], lh, lt, seed=si)
                        dp = gen_drg[si][1][i]
                        dm = gen_drg[si][-1][i]
                        role_plus = 1 if dp[2] else 0
                        role_minus = 1 if dm[2] else 0
                        r_acc["role_plus"][sk].append(role_plus)
                        r_acc["role_minus"][sk].append(role_minus)
                        # coin: bit=1 -> the + deranged gen counts, bit=0 -> the − deranged gen
                        r_acc["coin"][sk].append(role_plus if b == 1 else role_minus)
                        # keyem_role_s = f(drg+, drg-); keyem_coin_s = f in coin-s order
                        r_acc["keyem_role"][sk].append(1 if (dp[1] == "top" and dm[1] == "bridge") else 0)
                        if b == 1:
                            km = 1 if (dp[1] == "top" and dm[1] == "bridge") else 0
                        else:
                            km = 1 if (dm[1] == "top" and dp[1] == "bridge") else 0
                        r_acc["keyem_coin"][sk].append(km)

                # -------- (6c) breakage generations (C100) --------
                brk = {"1": 0, "-1": 0}
                coll = {"1": 0, "-1": 0}
                bridge_emit_minus = 0
                for sgn in (1, -1):
                    for mb in _mini(c100):
                        idl = [prompt_ids[i] for i in mb]
                        vecs = [alpha * sgn * dhat[i][lh] for i in mb]
                        gens = _gen_add(idl, lt, vecs)
                        for i, g in zip(mb, gens):
                            s = specs[i]
                            cat = _emit_cat(g, s)
                            ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                            if not ok:
                                brk[str(sgn)] += 1  # C100 are text-only-correct => flip
                            if not _has_any(g, s["surfaces"]):
                                coll[str(sgn)] += 1
                            if sgn == -1 and cat == "bridge":
                                bridge_emit_minus += 1
                            rows.append(_row(item_id=s["item_id"], probe="breakage",
                                             cell=[lh, lt], arm="real", sign=sgn, alpha=alpha,
                                             gen=g, correct=ok, emitted=cat, gold=s["gold_top"]))

                per_unit[ukey] = {
                    "alpha": alpha, "cell": [lh, lt], "completed": True,
                    "margin_real": m_acc["real"], "margin_coin": m_acc["coin"],
                    "margin_role": m_acc["role"], "margin_real_ties": m_acc["real_ties"],
                    "margin_coin_ties": m_acc["coin_ties"], "margin_role_ties": m_acc["role_ties"],
                    "mdiff_real": _mm(m_acc["mdiff_real"]),
                    "mdiff_role": {sk: _mm(m_acc["mdiff_role"][sk]) for sk in skeys},
                    "mdiff_coin": {sk: _mm(m_acc["mdiff_coin"][sk]) for sk in skeys},
                    "real_plus": r_acc["real_plus"], "real_minus": r_acc["real_minus"],
                    "coin": r_acc["coin"], "role_plus": r_acc["role_plus"],
                    "role_minus": r_acc["role_minus"], "keyem_real": r_acc["keyem_real"],
                    "keyem_role": r_acc["keyem_role"], "keyem_coin": r_acc["keyem_coin"],
                    "breakage": brk, "collapse": coll, "bridge_emit_minus": bridge_emit_minus,
                }
                completed_units.append([alpha, lh, lt])
                print("[s1] unit alpha=%g cell=(%d,%d) done: keyacc_real=%.3f "
                      "R+=%.3f R-=%.3f t=%.0fs"
                      % (alpha, lh, lt,
                         sum(m_acc["real"]) / max(1, len(m_acc["real"])),
                         sum(r_acc["real_plus"]) / max(1, m),
                         sum(r_acc["real_minus"]) / max(1, m),
                         time.time() - t0))

    except _B2Abort as e:
        aborted = True
        abort_reason = str(e)
        print("[s1] ABORT:", abort_reason)

    summary.update({"baseline_margin": _mm(baseline_margins),
                    "aborted": bool(aborted), "abort_reason": abort_reason,
                    "partial": bool(partial), "partial_reason": partial_reason,
                    "n_completed_units": len(completed_units),
                    "elapsed_s": time.time() - t0})

    return {
        "aborted": bool(aborted), "abort_reason": abort_reason,
        "partial": bool(partial), "partial_reason": partial_reason,
        "rows": [json.loads(json.dumps(r, default=str)) for r in rows],
        "summary": json.loads(json.dumps(summary, default=str)),
        "swept_item_ids": [specs[i]["item_id"] for i in swept],
        "c100_item_ids": [specs[i]["item_id"] for i in c100],
        "per_unit": json.loads(json.dumps(per_unit, default=str)),
        "completed_units": completed_units,
        "elapsed_s": time.time() - t0,
    }


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=21600)
def stage1_a10g(model_id, specs, bprime2_text_correct, batch_size, wall_cap_s):
    r = _stage1_body(model_id, specs, bprime2_text_correct, batch_size, wall_cap_s)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return r


def _stage1_gate(res):
    """Mechanical §5 decision rule from returned per-unit bit arrays. Computes the
    two-endpoint FIRE conjunctions (coin Bonferroni p<0.05/8 all seeds AND role
    p<0.05 all seeds AND Δ floors), the keying-replication check, the coin
    validity tripwires, and the KILL pooled-UB conjunction, then applies the
    ordered gate. Runner reports these numbers; interpretation is designer work."""
    aborted = bool(res.get("aborted", False))
    summary = res.get("summary", {})
    headroom_ok = bool(summary.get("headroom_ok", False))
    per_unit = res.get("per_unit", {})
    completed = [tuple(u) for u in res.get("completed_units", [])]
    m = summary.get("n_swept") or 0
    skeys = [str(si) for si in STAGE1_SEEDS]

    def _paired(real, ctrl):
        b = sum(1 for x, y in zip(real, ctrl) if x and not y)
        c = sum(1 for x, y in zip(real, ctrl) if (not x) and y)
        p = _bp_binom_sf_ge(b, b + c, 0.5)
        return {"b": b, "c": c, "n_discordant": b + c, "p_one_sided": p}

    any_coin_invalid = False
    coin_invalid_hits = []
    fire_minus = []
    fire_plus = []
    role_only_hits = []
    kill_all_below = True
    unit_reports = []

    for ukey, u in per_unit.items():
        completed_u = bool(u.get("completed", False))
        mr = u["margin_real"]
        nn = len(u["real_plus"])
        kr = sum(mr)
        ub_real = _bp_wilson(kr, len(mr), STAGE1_Z_KILL)[1] if mr else None
        # coin validity tripwires (margin-coin keyacc + emission-coin keyem)
        tripwire = {}
        for sk in skeys:
            mc = u["margin_coin"][sk]
            kec = u["keyem_coin"][sk]
            lb_mc = _bp_wilson(sum(mc), len(mc), STAGE1_Z_CTRL)[0] if mc else 0.0
            lb_kec = _bp_wilson(sum(kec), len(kec), STAGE1_Z_CTRL)[0] if kec else 0.0
            tripwire[sk] = {"keyacc_coin": (sum(mc) / len(mc) if mc else None),
                            "wilson_lb_keyacc_coin_z3_2790": lb_mc,
                            "keyem_coin": (sum(kec) / len(kec) if kec else None),
                            "wilson_lb_keyem_coin_z3_2790": lb_kec}
            if completed_u and (lb_mc > 0.5 or lb_kec > 0.5):
                any_coin_invalid = True
                coin_invalid_hits.append({"unit": ukey, "seed": sk,
                                          "lb_keyacc_coin": lb_mc, "lb_keyem_coin": lb_kec})

        endpoints = {}
        for e, real_key, role_key in (("minus", "real_minus", "role_minus"),
                                      ("plus", "real_plus", "role_plus")):
            real_e = u[real_key]
            per_seed = {}
            deltas = []
            ses = []
            p_coins = []
            p_roles = []
            for sk in skeys:
                coin_s = u["coin"][sk]
                role_es = u[role_key][sk]
                pc = _paired(real_e, coin_s)
                prole = _paired(real_e, role_es)
                delta = (pc["b"] - pc["c"]) / m if m else 0.0
                se = (_bp_math.sqrt(max(0.0, pc["b"] + pc["c"] - (pc["b"] - pc["c"]) ** 2 / m)) / m) if m else 0.0
                deltas.append(delta)
                ses.append(se)
                p_coins.append(pc["p_one_sided"])
                p_roles.append(prole["p_one_sided"])
                per_seed[sk] = {"rescue_coin": (sum(coin_s) / len(coin_s) if coin_s else None),
                                "rescue_role": (sum(role_es) / len(role_es) if role_es else None),
                                "paired_real_gt_coin": pc, "paired_real_gt_role": prole,
                                "delta_vs_coin": delta, "se": se}
            mean_delta = sum(deltas) / len(deltas)
            min_delta = min(deltas)
            max_se = max(ses)
            pooled_ub = mean_delta + STAGE1_Z_KILL * max_se
            cond_i = all(p < STAGE1_P_COIN for p in p_coins)
            cond_ii = all(p < STAGE1_P_ROLE for p in p_roles)
            cond_iii = (mean_delta >= STAGE1_DELTA_MEAN_FLOOR) and (min_delta >= STAGE1_DELTA_MIN_FLOOR)
            fire = completed_u and cond_i and cond_ii and cond_iii
            endpoints[e] = {
                "rescue_real": (sum(real_e) / len(real_e) if real_e else None),
                "per_seed": per_seed, "mean_delta_vs_coin": mean_delta,
                "min_delta_vs_coin": min_delta, "max_se": max_se, "pooled_ub95": pooled_ub,
                "cond_i_all_seeds_coin_p_lt_0.00625": cond_i,
                "cond_ii_all_seeds_role_p_lt_0.05": cond_ii,
                "cond_iii_delta_floors": cond_iii, "FIRE": fire}
            if fire and e == "minus":
                fire_minus.append(ukey)
            if fire and e == "plus":
                fire_plus.append(ukey)
            if completed_u and cond_i and cond_iii and not cond_ii:
                role_only_hits.append({"unit": ukey, "endpoint": e})
            if completed_u and pooled_ub >= STAGE1_KILL_UB:
                kill_all_below = False

        unit_reports.append({
            "unit": ukey, "alpha": u.get("alpha"), "cell": u.get("cell"),
            "completed": completed_u, "n": nn,
            "keyacc_real": (kr / len(mr) if mr else None),
            "wilson_ub95_keyacc_real_z1_6449": ub_real,
            "margin_coin_tripwire": tripwire,
            "keyacc_role": {sk: (sum(u["margin_role"][sk]) / len(u["margin_role"][sk])
                                 if u["margin_role"][sk] else None) for sk in skeys},
            "ties": {"real": u.get("margin_real_ties"), "coin": u.get("margin_coin_ties"),
                     "role": u.get("margin_role_ties")},
            "keyem_real": (sum(u["keyem_real"]) / len(u["keyem_real"]) if u["keyem_real"] else None),
            "endpoints": endpoints,
            "breakage_c100": u.get("breakage"), "collapse_c100": u.get("collapse"),
            "bridge_emit_minus_c100": u.get("bridge_emit_minus"),
        })

    # keying-replication check (spec §5 label 2): both α=1.0 cells completed AND
    # both UB95(keyacc_real@1.0) < 0.70
    a1_units = [u for u in per_unit.values() if abs(float(u.get("alpha", -1)) - 1.0) < 1e-9]
    a1_completed = [u for u in a1_units if u.get("completed")]
    a1_ubs = [_bp_wilson(sum(u["margin_real"]), len(u["margin_real"]), STAGE1_Z_KILL)[1]
              for u in a1_completed if u["margin_real"]]
    keying_not_replicated = (len(a1_units) == 2 and len(a1_completed) == 2
                             and len(a1_ubs) == 2 and all(ub < STAGE1_REPL_FLOOR for ub in a1_ubs))

    all8_done = len(completed) == 8
    all_kill = all8_done and kill_all_below

    if aborted or (not headroom_ok) or any_coin_invalid:
        label = "INSTRUMENT-INVALID"
    elif keying_not_replicated:
        label = "KEYING-NOT-REPLICATED"
    elif fire_minus:
        label = "PASS-INTEGRATION-RESCUE"
    elif fire_plus:
        label = "PASS-EMISSION-RESCUE-ONLY"
    elif role_only_hits:
        label = "ROLE-RESCUE-ONLY"
    elif all_kill:
        label = "KILL-NO-KEYED-RESCUE"
    else:
        label = "INCONCLUSIVE"

    return {
        "gate_label": label,
        "floors": {"repl": STAGE1_REPL_FLOOR, "delta_mean": STAGE1_DELTA_MEAN_FLOOR,
                   "delta_min": STAGE1_DELTA_MIN_FLOOR, "kill_ub": STAGE1_KILL_UB},
        "z": {"kill": STAGE1_Z_KILL, "ctrl": STAGE1_Z_CTRL},
        "p_thresholds": {"coin_bonferroni": STAGE1_P_COIN, "role": STAGE1_P_ROLE},
        "headroom_ok": headroom_ok, "aborted": aborted,
        "partial": bool(res.get("partial", False)),
        "n_completed_units": len(completed), "all8_units_completed": all8_done,
        "instrument_invalid_triggers": {
            "aborted": aborted, "not_headroom_ok": (not headroom_ok),
            "coin_tripwire_fired": any_coin_invalid, "coin_invalid_hits": coin_invalid_hits},
        "keying_not_replicated": keying_not_replicated,
        "alpha1_ub95_keyacc_real": a1_ubs,
        "fire_minus_units": fire_minus, "fire_plus_units": fire_plus,
        "role_only_hits": role_only_hits, "all9_kill": all_kill,
        "kill_all_units_below_ub": kill_all_below,
        "n_swept": m, "unit_reports": unit_reports,
    }


@app.local_entrypoint()
def stage1(dry_plan: bool = False, gpu: str = "A10G"):
    import hashlib
    import time

    def _sha_file(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    # ---- input pins (spec §2), ABORT on drift ----
    items_sha = _sha_file(_ROOT / "data/nsk1-clutrr/items.jsonl")
    head_sha = _sha_file(_ROOT / "data/nsk1-clutrr/headroom.jsonl")
    assert items_sha == STAGE1_ITEMS_PIN, "ABORT: items.jsonl sha mismatch %s" % items_sha
    assert head_sha == STAGE1_HEAD_PIN, "ABORT: headroom.jsonl sha mismatch %s" % head_sha

    specs = _build_specs_bprime2()  # spec §3 Step 0: verbatim B″ build (all asserts)
    n = len(specs)
    # byte-equality ASSERT: headroom-100 form-2 prompts == _build_specs_g2b f2_to
    g2b_specs, _vocab = _build_specs_g2b()
    g2b_f2 = {s["item_id"]: s["f2_to"] for s in g2b_specs}
    mine = {s["item_id"]: s["prompt"] for s in specs}
    mism = [iid for iid in g2b_f2 if g2b_f2[iid] != mine.get(iid)]
    assert not mism, "ABORT: form-2 prompt not byte-equal to g2b for %s" % mism[:5]
    print("[s1] byte-equality vs _build_specs_g2b f2_to: 100/100 OK")

    # ---- B″ text-only correctness vector for the repro gate (spec §3 Step 1) ----
    bp2_rows = _ROOT / "poc/nsk1/out/bprime2/bprime2_rows.jsonl"
    bprime2_text_correct = {}
    for l in bp2_rows.read_text().splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get("probe") == "text-only":
            bprime2_text_correct[r["item_id"]] = bool(r["correct"])
    assert len(bprime2_text_correct) >= 900, \
        "ABORT: B″ text-only reference incomplete (%d)" % len(bprime2_text_correct)
    # B″ swept ids for swept_overlap_bprime2 (report-only)
    bp2_summary = json.loads((_ROOT / "poc/nsk1/out/bprime2/bprime2_summary.json").read_text())
    bp2_swept = set(bp2_summary.get("swept_item_ids", []))

    n_units = len(STAGE1_ALPHA_LADDER) * len(STAGE1_CELLS)  # 8
    swept_plan = 200   # B″ measured |F| (spec §3 planning value)
    swept_worst = 300

    def _counts(nsw):
        gens = n + nsw * 8 * n_units + STAGE1_C100 * 2 * n_units
        fwd_donor = 2 * (nsw + STAGE1_C100)
        fwd_base = 2 * (nsw + STAGE1_C100)
        fwd_margin = nsw * 16 * n_units
        fwd = fwd_donor + fwd_base + fwd_margin
        return gens, fwd, (fwd_donor, fwd_margin, fwd_base)

    gens_p, fwd_p, brk_p = _counts(swept_plan)
    gens_w, fwd_w, brk_w = _counts(swept_worst)
    # GPU-h / $ planning band = spec §7 (STIPULATED-grade planning, not a measurement)
    gpuh_lo, gpuh_hi = 0.4, 1.5
    usd_lo, usd_hi = 0.5, 2.0

    print("=== nsk1 STAGE-1 free-generation keyed-rescue probe — PLAN (spec docs/next/nsk1-stage1-spec.md) ===")
    print("host                : R3 = %s  commit-pin %s" % (STAGE1_MODEL, STAGE1_PIN))
    print("items (covered)     : %d (858 items.jsonl covered + 100 headroom.jsonl)" % n)
    print("input pins OK       : items=%s… headroom=%s…" % (items_sha[:12], head_sha[:12]))
    print("cells               : %s  (ASSERT L=24; ℓt=16 both; ℓh∈{12,16})" % STAGE1_CELLS)
    print("α ladder (descending): %s  (1.0 anchor first; no α* selection)" % STAGE1_ALPHA_LADDER)
    print("derangement seeds   : %s (σ_a/σ_b/σ_c) ; sample/C100 seed %d" % (STAGE1_SEEDS, STAGE1_SAMPLE_SEED))
    print("units (cell×α)      : %d" % n_units)
    print("endpoints           : R− (integration, real −) + R+ (delivered-conclusion, real +)")
    print("gate stats          : coin p<%.5f ALL 3 seeds ; role p<%.2f ALL seeds ; Δmean≥%.2f & Δmin≥%.2f ; KILL pooled-UB<%.2f ; repl UB95<%.2f ; ctrl-LB tripwire z=%.4f"
          % (STAGE1_P_COIN, STAGE1_P_ROLE, STAGE1_DELTA_MEAN_FLOOR, STAGE1_DELTA_MIN_FLOOR, STAGE1_KILL_UB, STAGE1_REPL_FLOOR, STAGE1_Z_CTRL))
    print("planning |Swept|    : %d (=B″ measured |F|; actual = text-only failures, cap %d)" % (swept_plan, STAGE1_SWEEP_CAP))
    print("gens   @|Swept|=%d  : %d  (text-only %d + rescue %d + breakage %d)"
          % (swept_plan, gens_p, n, swept_plan * 8 * n_units, STAGE1_C100 * 2 * n_units))
    print("forwards@|Swept|=%d : %d  (donor %d + margins %d + baseline %d)"
          % (swept_plan, fwd_p, brk_p[0], brk_p[1], brk_p[2]))
    print("worst  @|Swept|=%d  : gens=%d forwards=%d" % (swept_worst, gens_w, fwd_w))
    print("GPU-h estimate      : %.1f–%.1f  |  $ estimate : $%.1f–$%.1f  (A10G fp32; spec §7 planning band)" % (gpuh_lo, gpuh_hi, usd_lo, usd_hi))
    print("HARD caps           : $25 / 10 GPU-h / 12 h wall  (in-container soft wall guard %ds)" % STAGE1_WALL_CAP_S)
    print("decision rule       : §5 — INSTRUMENT-INVALID → KEYING-NOT-REPLICATED → PASS-INTEGRATION-RESCUE → PASS-EMISSION-RESCUE-ONLY → ROLE-RESCUE-ONLY → KILL-NO-KEYED-RESCUE → INCONCLUSIVE")
    print("phase               : exploratory (quarantined, uncitable, flips no verdict)")

    caps_ok = (gpuh_hi <= 10 and usd_hi <= 25 and gens_w + fwd_w <= 120000)
    print("within caps (plan)  : %s" % caps_ok)

    if dry_plan:
        s0 = specs[0]
        # dry-plan build assertions: cells, α ladder, seeds, derangement fixed-point-free
        assert len(STAGE1_CELLS) == 2 and all(c[1] == 16 for c in STAGE1_CELLS), "cells not [(12,16),(16,16)]"
        assert STAGE1_ALPHA_LADDER == [1.0, 0.75, 0.5, 0.25], "alpha ladder drift"
        assert STAGE1_SEEDS == [20260712, 20260713, 20260714], "seed drift"
        for si in STAGE1_SEEDS:
            p = _bp_sattolo(swept_plan, si)
            assert all(p[k] != k for k in range(swept_plan)), "σ seed=%d not fixed-point-free @plan-n" % si
        print("\nDRY-PLAN ONLY — no GPU launched, $0 spent. All build asserts passed.")
        print("build-assert: cells=[(12,16),(16,16)] α=[1.0,0.75,0.5,0.25] seeds=%s (3 σ fixed-point-free @n=%d) OK"
              % (STAGE1_SEEDS, swept_plan))
        print("gens≈%d (~15.4k target) forwards≈%d (~26.8k target); within-caps=%s" % (gens_p, fwd_p, caps_ok))
        print("\n--- sample form-2 text-only prompt (item %s) ---\n%s" % (s0["item_id"], s0["prompt"]))
        print("\n--- donors (item %s) ---\nD_top   : %s\nD_bridge: %s\n[top=%s bridge=%s base=%s]"
              % (s0["item_id"], s0["d_top"], s0["d_bridge"], s0["top_surface"], s0["bridge_surface"], s0["base"]))
        print("\ncoin-bit samples (item %s):" % s0["item_id"])
        for si in STAGE1_SEEDS:
            for (lh, lt) in STAGE1_CELLS:
                print("  seed=%d cell=(%d,%d) b=%d" % (si, lh, lt, _bprime2_coin_bit(s0["item_id"], lh, lt, seed=si)))
        return

    if not caps_ok:
        raise SystemExit("ABORT: plan exceeds caps — not launching")

    t_launch = time.time()
    res = stage1_a10g.remote(STAGE1_MODEL, specs, bprime2_text_correct,
                             STAGE1_BATCH, STAGE1_WALL_CAP_S)
    wall_s = time.time() - t_launch

    outdir = _ROOT / "poc/nsk1/out/stage1"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = res.get("rows", [])
    with open(outdir / "stage1_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    gate = _stage1_gate(res)
    # swept_overlap_bprime2 (report-only, never gated)
    s1_swept = set(res.get("swept_item_ids", []))
    swept_overlap = len(s1_swept & bp2_swept)

    summary = dict(res.get("summary", {}))
    elapsed = res.get("summary", {}).get("elapsed_s", res.get("elapsed_s", 0.0)) or 0.0
    summary.update({
        "spec_ref": "docs/next/nsk1-stage1-spec.md",
        "gate": "NSK1-S1", "phase": "exploratory",
        "input_pins": {"items_jsonl_sha256": items_sha, "headroom_jsonl_sha256": head_sha},
        "verdict": gate,
        "swept_item_ids": res.get("swept_item_ids", []),
        "c100_item_ids": res.get("c100_item_ids", []),
        "swept_overlap_bprime2": swept_overlap,
        "wall_clock_s_local": round(wall_s, 1),
        "gpu_h_estimate": round(elapsed / 3600.0, 3),
        "usd_estimate": round(elapsed / 3600.0 * 1.10, 3),
        "n_rows": len(rows),
        "aborted": bool(res.get("aborted", False)), "abort_reason": res.get("abort_reason"),
        "partial": bool(res.get("partial", False)), "partial_reason": res.get("partial_reason"),
        "hard_caps": {"usd": 25, "gpu_h": 10, "wall_h": 12},
    })
    with open(outdir / "stage1_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    sha_rows = _sha_file(outdir / "stage1_rows.jsonl")
    sha_sum = _sha_file(outdir / "stage1_summary.json")
    print("\n=== nsk1 STAGE-1 RESULT (phase:exploratory) ===")
    print("aborted=%s partial=%s n_rows=%d n_completed_units=%d elapsed=%.0fs (GPU) / %.0fs (wall)"
          % (res.get("aborted"), res.get("partial"), len(rows),
             gate.get("n_completed_units"), elapsed, wall_s))
    print("swept_overlap_bprime2=%d/%d" % (swept_overlap, len(s1_swept)))
    print(json.dumps(gate, indent=1, sort_keys=True))
    print("MECHANICAL VERDICT (spec §5): %s" % gate["gate_label"])
    print("sha256 stage1_rows.jsonl    = %s" % sha_rows)
    print("sha256 stage1_summary.json  = %s" % sha_sum)
