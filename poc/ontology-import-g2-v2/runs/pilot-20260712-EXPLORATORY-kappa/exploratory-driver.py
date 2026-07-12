#!/usr/bin/env python3
"""EXPLORATORY driver (quarantined; see README-EXPLORATORY.txt).
Reuses the pinned harness verbatim except the preflight-pass gate."""
import importlib.util
import json
import os
import sys

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
HARNESS = os.path.join(REPO, "poc/ontology-import-g2-v2/run-ontg2v2.py")
EXPDIR = os.path.join(REPO, "poc/ontology-import-g2-v2/runs/"
                      "pilot-20260712-EXPLORATORY-kappa")

spec = importlib.util.spec_from_file_location("ontg2v2run", HARNESS)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

WORKDIRS = {}


def patched_require_preflight(jdir, pkey):
    os.makedirs(jdir, exist_ok=True)
    if pkey not in WORKDIRS:
        WORKDIRS[pkey] = mod.make_workdir("EXP%s" % pkey)
    return WORKDIRS[pkey]


mod._require_preflight = patched_require_preflight

# ---- (1) flakiness check: 4 fresh stateless repeats of cal:hedge-1 for pB ----
cfg = mod.JUDGE_CFG["pB"]
mod.verify_pins(cfg["kind"])
jdir = os.path.join(EXPDIR, cfg["id"])
workdir = patched_require_preflight(jdir, "pB")
log = mod.logger(jdir)
tmpl = mod.read_template()
sysp = mod.read_sysprompt()
cal = [r for r in mod.load_jsonl(
    "poc/ontology-import-g2-v2/calibration-hedge.jsonl")
    if r["id"] == "cal:hedge-1"][0]
mod._budget_check(EXPDIR, 4)
prompt = mod.assemble_prompt(cal["item"], tmpl)
reps = []
for k in range(1, 5):
    base = os.path.join(jdir, "hedge1-repeat", "rep%d" % k)
    r = mod.process_item(cfg, prompt, "rep%d" % k, base, workdir, sysp, log)
    reps.append({"rep": k, "answer": r["answer"]})
    print("HEDGE1_REPEAT pB rep%d answer=%s" % (k, r["answer"]), flush=True)
with open(os.path.join(EXPDIR, "hedge1-repeats-pB.json"), "w") as f:
    json.dump({"item": "cal:hedge-1", "expected": cal["expected"],
               "sanctioned_preflight_answer": "no", "repeats": reps}, f,
              indent=2)

# ---- (2) full pilot block per judge (harness phase_pilot VERBATIM) ----
for pk in ("pA", "pB"):
    print("EXP_PILOT %s start" % pk, flush=True)
    mod.phase_pilot(pk, EXPDIR)

# ---- (3) mechanical metrics (pinned functions; NOT phase_pilotgate: no
#          verdict-shaped artifact is minted from exploratory labels) ----
pm = mod._pilot_metrics(EXPDIR)
k = mod._kappa(pm["table"])
fs = {pk: (pm["hedgeflip_%s" % pk]["n_false_sat"]
           / pm["hedgeflip_%s" % pk]["n_labelled"]
           if pm["hedgeflip_%s" % pk]["n_labelled"] else 1.0)
      for pk in ("pA", "pB")}
out = {"EXPLORATORY": True, "kappa_a3": k, "metrics": pm,
       "hedgeflip_false_sat": fs,
       "gate_reference": {"kappa_a3_min": 0.40, "cal_correct_min": 12,
                          "decisive_min_per_judge": 36,
                          "hedgeflip_false_sat_max_per_judge": 0.25}}
with open(os.path.join(EXPDIR, "exploratory-pilot-metrics.json"), "w") as f:
    json.dump(out, f, indent=2, sort_keys=True)
print("EXP_METRICS %s" % json.dumps(
    {"kappa_a3": k, "table": pm["table"], "cal_correct": pm["cal_correct"],
     "decisive_pA": pm["decisive_pA"], "decisive_pB": pm["decisive_pB"],
     "hedgeflip_false_sat": fs}, sort_keys=True), flush=True)
print("EXP_DONE", flush=True)
