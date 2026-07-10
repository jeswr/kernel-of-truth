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
