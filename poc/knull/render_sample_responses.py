#!/usr/bin/env python3
"""Render poc/knull/sample-responses.json -> poc/knull/sample-responses.md
(side-by-side v3 vs v4 actual model outputs). PROVISIONAL, illustrative.

Optional argv[1]: artifact basename (default "sample-responses") — the modal
wrapper (poc/knull/modal/modal_knull_samples.py) passes
"sample-responses-mock" so a transport smoke never overwrites the real files.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = sys.argv[1] if len(sys.argv) > 1 else "sample-responses"
data = json.load(open(os.path.join(HERE, BASE + ".json"), encoding="utf-8"))
IS_MOCK = "MOCK" in data.get("status", "")

L = []
L.append("# knull plain-store sample responses - ACTUAL small-model outputs, v3 vs v4")
L.append("")
if IS_MOCK:
    L.append("> **MOCK TRANSPORT SMOKE** - every 'output' below is a stub;")
    L.append("> NO model was loaded and NOTHING here is a generation. This")
    L.append("> file exists only to prove the transport + rendering path.")
    L.append("")
L.append("> STATUS: **PROVISIONAL, illustrative**. Every response below is the")
L.append("> RAW, UNEDITED output of an actual model generation - nothing is")
L.append("> paraphrased, cherry-picked among samples, or re-rolled (greedy")
L.append("> decoding admits exactly one output per input). These are")
L.append("> small-model generations for illustration of how the two control")
L.append("> stores read in use; they are NOT verdict-bearing and NOT part of")
L.append("> any pre-registered Phase-X harness.")
L.append(">")
L.append("> **Model:** `%s` | **Decoding:** %s, max_new_tokens=%d, dtype=%s,"
         % (data["model"], data["decode"]["strategy"],
            data["decode"]["max_new_tokens"], data["decode"]["dtype"]))
L.append("> device=%s, stop=%s, seed: %s."
         % (data["decode"]["device"], data["decode"].get("stop", "eos"),
            data["decode"].get("seed", "n/a")))
if "execution" in data:
    L.append(">")
    L.append("> **Execution path:** %s" % data["execution"]["path"])
    L.append("> ONNX graph sha256 `%s`. %s"
             % (data["execution"]["onnx_sha256"], data["execution"]["patch"]))
L.append(">")
L.append("> **Context design:** %s" % data["context_design"])
L.append(">")
for tag in ("v3", "v4"):
    s = data["stores"][tag]
    L.append("> **%s store:** `%s` sha256 `%s`" % (tag, s["path"], s["sha256"]))
L.append(">")
L.append("> Generated %s by the Fable agent session (maintainer issue 17)." % data["date"])
if "harness" in data:
    L.append("> Harness: %s" % data["harness"])
else:
    L.append("> Harness: `poc/knull/run_sample_responses_onnx.py` (prompt set +")
    L.append("> context design single-sourced from `run_sample_responses.py`).")
if data.get("model_revision"):
    L.append("> Model revision pin: `%s`." % data["model_revision"])
L.append("")
L.append("The v3 store is the Option-B concise store that FAILED the ASM-0703")
L.append("gate on set-level template monotony (GPT-5.6 8/10, Haiku 4/10); the")
L.append("v4 store is the frame-variation re-authoring (option A). Each prompt")
L.append("below is answered twice by the same model under identical settings;")
L.append("the ONLY changed bytes between the two runs are the injected")
L.append("definition texts (same concept labels in both arms).")
L.append("")

for i, row in enumerate(data["results"], 1):
    L.append("---")
    L.append("")
    L.append("## %d. %s" % (i, row["question"]))
    L.append("")
    L.append("*Injected store entries (same labels, both arms):* `%s`"
             % "`, `".join(row["labels"]))
    L.append("")
    for tag, name in (("v3", "v3 store (Option-B concise, gate-FAILED)"),
                      ("v4", "v4 store (frame-variation retry)")):
        L.append("### with the %s" % name)
        L.append("")
        L.append("```text")
        L.append(row["outputs"][tag])
        L.append("```")
        L.append("")

L.append("---")
L.append("")
n = len(data["results"])
kind = "stub placeholders (MOCK)" if IS_MOCK else "actual generations"
L.append("*End of illustrative sample set (%d prompts x 2 stores = %d %s)."
         % (n, 2 * n, kind))
L.append("Raw JSON with shas: `poc/knull/%s.json`.*" % BASE)

out = os.path.join(HERE, BASE + ".md")
open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote %s (%d prompts)" % (out, len(data["results"])))
