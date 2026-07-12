#!/usr/bin/env python3
"""knull v3-vs-v4 sample-responses harness (maintainer issue 17, deliverable 2).

PROVISIONAL, ILLUSTRATIVE instrument - NOT a pre-registered Phase-X harness,
NOT verdict-bearing. Its sole purpose is to show the maintainer what a small
LLM ACTUALLY OUTPUTS when handed the plain-definition control store as
context: for each of 8 representative natural-language prompts, the model is
run twice - once with the relevant v3 (Option-B concise) store entries
injected as context, once with the SAME labels' v4 (frame-variation retry)
entries - and the RAW generation is captured verbatim both times.

Model + decode settings (pinned, disclosed in every artifact):
  model      HuggingFaceTB/SmolLM2-360M-Instruct (CPU, float32)
  decoding   GREEDY (do_sample=False), max_new_tokens=200, no sampling
             params in play; deterministic given this software stack
  context    the store entries for a fixed per-prompt label set (identical
             label set across the two arms - the only changed bytes are the
             definition texts), rendered as a reference list in the system
             message, headwords SHOWN (this is a usage illustration, not the
             blind ASM-0703 gate)

Outputs:
  poc/knull/sample-responses.json  (raw, with shas + settings)
  stdout progress

Usage:
  python3 poc/knull/run_sample_responses.py
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

MODEL_ID = "HuggingFaceTB/SmolLM2-360M-Instruct"
MAX_NEW_TOKENS = 200

# 8 representative prompts; each names the store labels injected as context.
# Label sets are IDENTICAL across the v3 and v4 arms by construction.
PROMPTS = [
    {"id": "condolence",
     "q": "My friend's father just died. What should I say to her?",
     "labels": ["condolence (the words)", "grieving", "death (the event)",
                "friend (X is a friend of Y)", "father", "sad"]},
    {"id": "lie-vs-promise",
     "q": "What is the difference between a lie and a promise?",
     "labels": ["lie (the words)", "promise (the words)", "liar",
                "trustworthy", "believe (X believes Y)"]},
    {"id": "fish-animal",
     "q": "Is a fish an animal? Explain briefly.",
     "labels": ["fish", "animal", "alive", "water"]},
    {"id": "archived-bookmark",
     "q": "I archived a bookmark by accident. Is it gone forever?",
     "labels": ["archived (bookmark boolean property)", "bookmark", "lost",
                "find (X finds Y)"]},
    {"id": "cat-kind",
     "q": "Could my cat have been a dog instead? What kind of thing is a cat?",
     "labels": ["kind (gufo:Kind, sortal type)", "cat", "dog", "animal",
                "change (the event)"]},
    {"id": "run-vs-walk",
     "q": "How is running different from walking?",
     "labels": ["run", "walk", "jump", "ground"]},
    {"id": "celebrate-birth",
     "q": "Why do people celebrate when a baby is born?",
     "labels": ["celebration", "birth (the event)", "happy", "gift", "event"]},
    {"id": "good-teacher",
     "q": "What makes someone a good teacher?",
     "labels": ["teacher", "learn (X learns Y)", "help (X helps Y)",
                "helpful (of a someone)", "remember (X remembers Y)"]},
]


def sha256_file(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def load_store(tag):
    path = os.path.join(HERE, "inputs-%s" % tag, "plain-authored.json")
    with open(path, encoding="utf-8") as f:
        store = json.load(f)
    return path, sha256_file(path), store["definitions"]


def build_messages(defs, item):
    ref = "\n".join("- %s: %s" % (lab, defs[lab]) for lab in item["labels"])
    system = ("You are a helpful assistant. Use the following reference "
              "definitions when answering.\n\nReference definitions:\n"
              + ref)
    return [{"role": "system", "content": system},
            {"role": "user", "content": item["q"]}]


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(0)
    torch.set_num_threads(max(1, os.cpu_count() - 0))

    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID,
                                                 torch_dtype=torch.float32)
    model.eval()

    arms = {}
    for tag in ("v3", "v4"):
        path, sha, defs = load_store(tag)
        arms[tag] = {"path": os.path.relpath(path, os.path.dirname(HERE)),
                     "sha256": sha, "defs": defs}
        for item in PROMPTS:
            for lab in item["labels"]:
                if lab not in defs:
                    sys.exit("missing label %r in %s store" % (lab, tag))

    results = []
    for item in PROMPTS:
        row = {"id": item["id"], "question": item["q"],
               "labels": item["labels"], "outputs": {}}
        for tag in ("v3", "v4"):
            msgs = build_messages(arms[tag]["defs"], item)
            ids = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                          return_tensors="pt")
            t0 = time.time()
            with torch.no_grad():
                out = model.generate(ids, max_new_tokens=MAX_NEW_TOKENS,
                                     do_sample=False,
                                     pad_token_id=tok.eos_token_id)
            text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
            row["outputs"][tag] = text.strip()
            print("[%s/%s] %d prompt toks -> %d new toks in %.1fs"
                  % (item["id"], tag, ids.shape[1],
                     out.shape[1] - ids.shape[1], time.time() - t0),
                  flush=True)
        results.append(row)

    artifact = {
        "schema": "kot-knull-sample-responses/1",
        "status": "PROVISIONAL illustrative generations - actual raw model "
                  "outputs, not verdict-bearing, not a pre-registered "
                  "Phase-X harness",
        "model": MODEL_ID,
        "decode": {"strategy": "greedy (do_sample=False)",
                   "max_new_tokens": MAX_NEW_TOKENS,
                   "dtype": "float32", "device": "cpu",
                   "torch_manual_seed": 0},
        "context_design": "per-prompt fixed label set, identical across arms;"
                          " store entries rendered as a reference list in the"
                          " system message; headwords shown (usage"
                          " illustration, not the blind gate)",
        "stores": {t: {k: v for k, v in arms[t].items() if k != "defs"}
                   for t in arms},
        "date": "2026-07-11",
        "results": results,
    }
    opath = os.path.join(HERE, "sample-responses.json")
    with open(opath, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=1, sort_keys=False)
        f.write("\n")
    print("wrote %s" % opath)


if __name__ == "__main__":
    main()
