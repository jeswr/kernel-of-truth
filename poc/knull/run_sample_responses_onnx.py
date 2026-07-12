#!/usr/bin/env python3
"""knull v3-vs-v4 sample-responses harness - ONNX execution path.

PROVISIONAL, ILLUSTRATIVE instrument - NOT a pre-registered Phase-X harness,
NOT verdict-bearing. Same design as run_sample_responses.py (same 8 prompts,
same per-prompt label sets, same context rendering, greedy decoding), but
executed WITHOUT torch/transformers, which cannot be installed on this box
(python 3.9 + 2.5 GB free disk):

  model     HuggingFaceTB/SmolLM2-360M-Instruct, the repo's own fp32 ONNX
            export (onnx/model.onnx, sha256 pinned below), i.e. the SAME
            weights as the safetensors checkpoint, exported to fp32
  runtime   onnxruntime 1.19.2 CPU EP, 2 intra-op threads
  patch     the export writes softcap=0.0 on all 32 GroupQueryAttention
            nodes; ORT 1.19 predates that attribute name and refuses the
            graph. softcap=0.0 is the operator DEFAULT (softcapping
            disabled), so the attribute is a no-op; we strip it IN MEMORY
            (no bytes of the cached model change on disk) and build the
            session from the patched buffer. Semantics identical.
  decoding  GREEDY (argmax at every step), max_new_tokens=200, stop at
            <|im_end|>; deterministic given this software stack
  template  the repo's own chat template (tokenizer_config.json), applied
            verbatim: <|im_start|>{role}\n{content}<|im_end|>\n ... +
            <|im_start|>assistant\n

Outputs: poc/knull/sample-responses.json (raw, with shas + settings)
Usage:   nice -n 10 python3 poc/knull/run_sample_responses_onnx.py
"""
import hashlib
import json
import os
import sys
import time

import numpy as np
import onnx
import onnxruntime as ort
from tokenizers import Tokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
# Single-source the prompt set + store loader from the torch-path harness.
sys.path.insert(0, HERE)
from run_sample_responses import PROMPTS, MODEL_ID, MAX_NEW_TOKENS, \
    load_store, sha256_file  # noqa: E402

SNAP = ("/home/ec2-user/.cache/huggingface/hub/"
        "models--HuggingFaceTB--SmolLM2-360M-Instruct/snapshots/"
        "a10cc1512eabd3dde888204e902eca88bddb4951")
ONNX_PATH = os.path.join(SNAP, "onnx", "model.onnx")
TOK_PATH = os.path.join(SNAP, "tokenizer.json")
IM_START, IM_END = "<|im_start|>", "<|im_end|>"
EOS_ID = 2  # <|im_end|> per generation_config.json


def build_context_text(defs, item):
    # Byte-identical context design to run_sample_responses.build_messages.
    ref = "\n".join("- %s: %s" % (lab, defs[lab]) for lab in item["labels"])
    return ("You are a helpful assistant. Use the following reference "
            "definitions when answering.\n\nReference definitions:\n" + ref)


def chat_text(system, user):
    # tokenizer_config.json chat_template, applied verbatim.
    return ("%ssystem\n%s%s\n%suser\n%s%s\n%sassistant\n"
            % (IM_START, system, IM_END, IM_START, user, IM_END, IM_START))


def make_session():
    m = onnx.load_model(ONNX_PATH)
    removed = 0
    for node in m.graph.node:
        if node.op_type == "GroupQueryAttention":
            keep = [a for a in node.attribute if a.name != "softcap"]
            for a in node.attribute:
                if a.name == "softcap" and a.f != 0.0:
                    sys.exit("softcap %r != 0.0 - refusing no-op strip" % a.f)
            removed += len(node.attribute) - len(keep)
            del node.attribute[:]
            node.attribute.extend(keep)
    buf = m.SerializeToString()
    del m
    so = ort.SessionOptions()
    so.intra_op_num_threads = 2
    so.inter_op_num_threads = 1
    sess = ort.InferenceSession(buf, so, providers=["CPUExecutionProvider"])
    del buf
    return sess, removed


def generate(sess, tok, prompt_text, kv_heads, head_dim, n_layers):
    ids = tok.encode(prompt_text).ids
    past = {("past_key_values.%d.%s" % (i, kv)):
            np.zeros((1, kv_heads, 0, head_dim), dtype=np.float32)
            for i in range(n_layers) for kv in ("key", "value")}
    out_names = [o.name for o in sess.get_outputs()]
    in_names = {i.name for i in sess.get_inputs()}
    new_ids = []
    cur = ids
    total = len(ids)
    for _ in range(MAX_NEW_TOKENS):
        feed = {"input_ids": np.array([cur], dtype=np.int64),
                "attention_mask": np.ones((1, total), dtype=np.int64)}
        if "position_ids" in in_names:
            start = total - len(cur)
            feed["position_ids"] = np.arange(start, total,
                                             dtype=np.int64)[None, :]
        feed.update(past)
        outs = sess.run(out_names, feed)
        by = dict(zip(out_names, outs))
        nxt = int(np.argmax(by["logits"][0, -1]))
        past = {("past_key_values.%d.%s" % (i, kv)):
                by["present.%d.%s" % (i, kv)]
                for i in range(n_layers) for kv in ("key", "value")}
        if nxt == EOS_ID:
            break
        new_ids.append(nxt)
        cur = [nxt]
        total += 1
    return len(ids), tok.decode(new_ids, skip_special_tokens=True)


def main():
    with open(os.path.join(SNAP, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    n_layers = cfg["num_hidden_layers"]
    kv_heads = cfg["num_key_value_heads"]
    head_dim = cfg["hidden_size"] // cfg["num_attention_heads"]

    tok = Tokenizer.from_file(TOK_PATH)
    onnx_sha = sha256_file(ONNX_PATH)
    print("building session (in-memory softcap strip)...", flush=True)
    sess, removed = make_session()
    print("session ready (%d no-op softcap attrs stripped)" % removed,
          flush=True)

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
            text = chat_text(build_context_text(arms[tag]["defs"], item),
                             item["q"])
            t0 = time.time()
            n_prompt, out = generate(sess, tok, text, kv_heads, head_dim,
                                     n_layers)
            row["outputs"][tag] = out.strip()
            print("[%s/%s] %d prompt toks -> %d chars in %.1fs"
                  % (item["id"], tag, n_prompt, len(out), time.time() - t0),
                  flush=True)
        results.append(row)

    artifact = {
        "schema": "kot-knull-sample-responses/1",
        "status": "PROVISIONAL illustrative generations - actual raw model "
                  "outputs, not verdict-bearing, not a pre-registered "
                  "Phase-X harness",
        "model": MODEL_ID,
        "execution": {
            "path": "repo fp32 ONNX export (onnx/model.onnx) via onnxruntime "
                    "%s CPU EP; torch/transformers not installable on this "
                    "box (python 3.9, 2.5 GB free disk)" % ort.__version__,
            "onnx_sha256": onnx_sha,
            "patch": "softcap=0.0 attribute stripped in memory from 32 "
                     "GroupQueryAttention nodes (operator default = 0.0 = "
                     "disabled; semantics identical; cached model unchanged "
                     "on disk)",
        },
        "decode": {"strategy": "greedy (stepwise argmax)",
                   "max_new_tokens": MAX_NEW_TOKENS,
                   "dtype": "float32", "device": "cpu",
                   "stop": "<|im_end|> (id 2)",
                   "seed": "none needed - greedy decoding is deterministic"},
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
