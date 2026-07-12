#!/usr/bin/env python3
"""build-v2-materials.py -- DETERMINISTIC one-shot builder of the g2-import-v2
instrument files (design doc docs/next/design/g2-import-v2-repair.md sections
2-4; registry g2-import-v2, design-doc section 9 step 2). Consumes the v1
arm/probe materials BY PIN (byte-identical, never regenerated) and writes ONLY
the NEW v2 instrument files:

  prompt-template-v2.txt        sentence-force rubric (design section 2, verbatim)
  calibration-hedge.jsonl       6 hedge-calibration items (design section 3a)
  probes-hedgeflip-a2.jsonl     10 hedge-flip probes, A2 register (section 3b)
  probes-hedgeflip-a3.jsonl     10 hedge-flip probes, A3 register (section 3b)
  pilot-manifest.json           40 stratified pilot ids + kappa gate + OC (section 4)
  materials/manifest.json       fresh deterministic per-judge order seeds

No RNG, no clock: every selection/order is sha256-derived from pinned ids and
the fixed date string 2026-07-12 (the design date, not the build clock).
Fail-closed: any pin mismatch or construction anomaly aborts (ERR_ONTG2V2_*).
"""
import hashlib
import json
import os
import sys

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
BASE = os.path.join(REPO, "poc/ontology-import-g2-v2")
V1MAT = os.path.join(REPO, "poc/ontology-import-g2/materials")
DATE = "2026-07-12"

# v1 pins consumed here (byte-identical; regeneration = pin break, ASM-1560)
V1_PINS = {
    "poc/ontology-import-g2/materials/arm-a2-bfo-sumo.jsonl":
        "13ce9e116a44dca072a4e9b8f4103d4025c1fdc1527a67e321195b55a9c92bd7",
    "poc/ontology-import-g2/materials/arm-a3-bfo-sumo-framenet.jsonl":
        "4600941ae080991071e6ff4de2a97cd450b3ad4bc8ed8c63686729f78855d3e3",
    "poc/ontology-import-g2/materials/probes-a1.jsonl":
        "c19576730437b1bdc3a4f95dd63892910aecf242d04fe4b3707277835af3aaa7",
    "poc/ontology-import-g2/materials/probes-a2.jsonl":
        "516efb1df208e57d3b32d1d5fb435d4e88c4aa3933a29b9038f39999154b540c",
    "poc/ontology-import-g2/materials/probes-a3.jsonl":
        "76c8d389d4980f99d088edb36e9b246b91cee3daf4f3df09de046ada9774a175",
    "poc/g2/materials/items.jsonl":
        "7a4728840550227703338880a79f61491a3c93e5022f07215631f6caa7077008",
}


def die(msg):
    sys.stderr.write("ERR_ONTG2V2_BUILD: %s\n" % msg)
    sys.exit(2)


def sha_str(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


for rel, want in V1_PINS.items():
    got = file_sha(os.path.join(REPO, rel))
    if got != want:
        die("pin %s sha %s != %s" % (rel, got, want))

# ---------------- 1. prompt-template-v2.txt (design section 2, verbatim) ----
TEMPLATE = """You are an independent judge of short statements about the meaning of everyday English words. Judge ONLY by the ordinary meaning of the quoted concept (the parenthetical, if any, tells you which sense of the word is meant). Do not use any tools. This is a single standalone question.

{{ITEM}}

A statement may contain several sentences of different strengths. Read each sentence at its own stated strength:
- A sentence with no hedge ("Every ...", "In every case ...", "Whenever ...") claims that the concept's ordinary meaning guarantees it in ALL normal cases. It is true only if that guarantee holds.
- A sentence hedged with "Normally" or "Typically" claims only how things usually or characteristically are for this concept. It is true if ordinary meaning makes it the usual or characteristic case; the existence of exceptions does NOT make it false. It is false if it misdescribes even the usual case.

Question: Is the whole statement true of the concept's ordinary meaning, with every sentence read at its own stated strength?
Answer "yes" only if EVERY sentence is true at its stated strength.
Answer "no" if ANY sentence is false at its stated strength — but never answer "no" merely because a "Normally"/"Typically" sentence has exceptions.
Answer with a single raw JSON object and nothing else — no markdown fence, no prose:
{"answer": "yes"} — every sentence is true at its stated strength
{"answer": "no"} — some sentence is false at its stated strength
{"answer": "cannot-say"} — only if the statement is genuinely undecidable for this concept
"""
with open(os.path.join(BASE, "prompt-template-v2.txt"), "w",
          encoding="utf-8") as f:
    f.write(TEMPLATE)

# ---------------- 2. calibration-hedge.jsonl (design section 3a) ------------
# cal:hedge-1 REPAIRED 2026-07-12 (design section 11.5): the original head
# "Every bird hatches from an egg." is a BIOLOGICAL universal, not an
# ordinary-meaning guarantee -- judge-pB answered "no" systematically (the
# sanctioned preflight miss + 4/4 stateless repeats), a DEFENSIBLE strict
# reading of the rubric's own "ordinary meaning guarantees it" standard.
# The item, not the judge, was unsound. Repaired head is analytic ("Every
# bird is an animal."); the exercised channel (hedged-true-despite-
# exceptions, penguins) is unchanged.
CAL = [
    {"id": "cal:hedge-1", "expected": "yes",
     "item": "Concept: “bird”\nStatement: Every bird is an animal. "
             "Normally a bird can fly."},
    {"id": "cal:hedge-2", "expected": "no",
     "item": "Concept: “triangle”\nStatement: Every triangle has "
             "exactly three sides. Normally a triangle has four corners."},
    {"id": "cal:hedge-3", "expected": "yes",
     "item": "Concept: “chair”\nStatement: In every case of a "
             "chair, it is made to be sat on. Normally a chair has legs."},
    {"id": "cal:hedge-4", "expected": "no",
     "item": "Concept: “knife”\nStatement: Every knife is made of "
             "metal. Normally a knife can cut."},
    {"id": "cal:hedge-5", "expected": "yes",
     "item": "Concept: “letter (written message)”\nStatement: In "
             "every case of a letter, someone wrote it. Typically it is "
             "meant for someone to read."},
    {"id": "cal:hedge-6", "expected": "no",
     "item": "Concept: “gift”\nStatement: In every case of a gift, "
             "someone gives it. Typically the one who receives it must pay "
             "the giver for it."},
]
with open(os.path.join(BASE, "calibration-hedge.jsonl"), "w",
          encoding="utf-8") as f:
    for r in CAL:
        f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

# ---------------- 3. hedge-flip probes (design section 3b) ------------------
# Construction: keep the unhedged head INTACT (and true), replace everything
# from the FIRST hedge marker on with a wrong-usual-case hedged tail (same
# absurd register as the v1 deranged probes). Expected "no" under the v2
# sentence-force rubric: the hedged sentence misdescribes even the usual case.
TAILS_NORMALLY = [
    "Normally this is done by a place far away.",
    "Normally it is a color that can be heard from far away.",
    "Normally it happens only to things that do not exist.",
    "Normally it is itself a place far away — somewhere one could walk to.",
    "Normally it is done by a time of day, not by anyone.",
]
TAILS_TYPICALLY = [
    "Typically this is done by a place far away.",
    "Typically it is a color that can be heard from far away.",
    "Typically it happens only to things that do not exist.",
    "Typically it is itself a place far away — somewhere one could walk to.",
    "Typically it is done by a time of day, not by anyone.",
]
ARM_SRC = {"a2": "arm-a2-bfo-sumo.jsonl", "a3": "arm-a3-bfo-sumo-framenet.jsonl"}
N_HF = 10
hf_ids = {}
for arm, fn in sorted(ARM_SRC.items()):
    rows = load_jsonl(os.path.join(V1MAT, fn))
    hedged = [r for r in rows
              if ("Normally" in r["item"] or "Typically" in r["item"])]
    if len(hedged) < N_HF:
        die("%s: only %d hedged items" % (arm, len(hedged)))
    hedged.sort(key=lambda r: sha_str(r["id"] + "|ontg2v2/hedgeflip|" + arm))
    out = []
    for k, src in enumerate(hedged[:N_HF]):
        text = src["item"]
        idx = min([i for i in (text.find("Normally"), text.find("Typically"))
                   if i >= 0])
        head = text[:idx].rstrip()
        if not head.endswith("."):
            die("%s %s: head does not end with '.'" % (arm, src["id"]))
        # A2 items carry "Normally" only; A3 alternates both markers, matching
        # each arm's own hedge register (no cross-arm register leak).
        tail = (TAILS_NORMALLY[k % 5] if arm == "a2"
                else (TAILS_NORMALLY if k % 2 == 0 else TAILS_TYPICALLY)[k % 5])
        out.append({"id": "ontg2v2:hf:%s:%03d" % (arm, k),
                    "arm": src["arm"], "expected": "no",
                    "form": src["form"], "rule": src["rule"],
                    "source_id": src["id"],
                    "item": head + " " + tail})
    hf_ids[arm] = [r["id"] for r in out]
    with open(os.path.join(BASE, "probes-hedgeflip-%s.jsonl" % arm), "w",
              encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

# ---------------- 4. pilot-manifest.json (design section 4) -----------------
items = load_jsonl(os.path.join(REPO, "poc/g2/materials/items.jsonl"))
by_rule = {"R1": [], "R3": [], "R4": []}
for r in items:
    by_rule[r["rule"]].append(r["id"])
STRATA = {"R3": 20, "R4": 16, "R1": 4}     # proportional to 42/34/8 at n=40
pilot_ids = []
for rule in ("R1", "R3", "R4"):
    ids = sorted(by_rule[rule], key=lambda i: sha_str(i + "|ontg2v2/pilot"))
    k = STRATA[rule]
    if len(ids) < k:
        die("stratum %s: %d < %d" % (rule, len(ids), k))
    pilot_ids.extend(ids[:k])
pilot_ids.sort()
# doubled 4 -> 8 (design section 11.4): the known-answer channels are now
# load-bearing instrument evidence; at n=4 the <=1/4 gate passes a
# coin-flipping judge 31% of the time, at n=8 the <=2/8 gate passes it 15%.
pilot_flip = sorted(hf_ids["a3"],
                    key=lambda i: sha_str(i + "|ontg2v2/pilotflip"))[:8]
pilot_manifest = {
    "schema": "ontg2v2-pilot/1",
    "build_date": DATE,
    "n_pilot_items": 40,
    "strata": STRATA,
    "selection_rule": "within each rule stratum of poc/g2/materials/"
                      "items.jsonl, ids sorted ascending by "
                      "sha256(id + '|ontg2v2/pilot') hex; take the first k "
                      "(R3=20, R4=16, R1=4); design doc section 4",
    "ids": pilot_ids,
    "hedgeflip_probe_ids": pilot_flip,
    "hedgeflip_selection_rule": "probes-hedgeflip-a3.jsonl ids sorted "
                                "ascending by sha256(id + '|ontg2v2/"
                                "pilotflip') hex; first 8 (doubled from 4, "
                                "design section 11.4)",
    "order_seed": "ontg2v2/pilot|judge-<pk>|a3|%s" % DATE,
    "gate": {
        "cal_correct_min": 12,
        "ac1_a3_min": 0.65,
        "decisive_min_per_judge": 36,
        "hedgeflip_false_sat_max_per_judge": 0.25,
        "note": "kappa-paradox redesign 2026-07-12 (design section 11): the "
                "gated pair statistic is Gwet AC1, prevalence-robust; Cohen "
                "kappa is co-reported for cross-record continuity, NEVER "
                "gated. ANY failure = STOP before any full-arm call; "
                "mechanical verdict INSTRUMENT-INVALID with the pilot "
                "channel named; pilot labels are instrument evidence only, "
                "discarded from all scoring",
    },
    "agreement_convention": "Gwet AC1 over the both-decisive yes/no pair "
                            "table of the 40 pilot items (identical function "
                            "to the pinned full-run analysis; pe_gamma = "
                            "2*pi*(1-pi) <= 0.5, never degenerate for n > 0). "
                            "Co-reported, never gate substitutes: Cohen kappa "
                            "(v1 convention, pe == 1 implies po == 1 -> kappa "
                            ":= 1.0), PABAK = 2*po - 1, positive/negative "
                            "specific agreement p_pos/p_neg, the raw 2x2 "
                            "table, both yes-marginals, and the marginal-"
                            "matched independence-ceiling AC1 (0.5873 at the "
                            "measured exploratory operating marginals 35/40, "
                            "31/40) -- the gated 0.65 must clear that "
                            "ceiling, which any threshold <= 0.60 does not",
    "ac1_threshold_justification": "0.65 (design section 11.3): (i) above "
                                   "the independence-ceiling AC1 0.587 at "
                                   "the measured v2 operating marginals -- "
                                   "independent judges pass AC1>=0.55 64% "
                                   "and AC1>=0.60 46% of the time at n=40, "
                                   "AC1>=0.65 30%; (ii) tighter than the "
                                   "retired kappa gate's carried-over "
                                   "stringency (kappa 0.40 at v1 A3 "
                                   "marginals <=> AC1 0.51); (iii) between "
                                   "measured-broken v1 A3 (0.417; 0.529 on "
                                   "the matched 40) and measured-healthy "
                                   "unhedged A1 (0.744); (iv) at the pilot "
                                   "marginals it demands raw agreement >= "
                                   "31/40, strictly beating the item-matched "
                                   "v1 subset's 30/40. Disclosed: the "
                                   "quarantined 2026-07-12 EXPLORATORY pilot "
                                   "measured AC1 0.578 and FAILS this gate; "
                                   "the threshold was not shopped to pass "
                                   "known data",
    "operating_characteristics": {
        "model": "per-item iid: pA ~ Bernoulli(m); pB = pA with prob a, "
                 "flipped otherwise; Gwet AC1 over the n=40 table; Monte "
                 "Carlo 200000 reps, numpy default_rng(20260712) "
                 "multinomial, computed at redesign time (design section "
                 "11.6); m pinned at BOTH 58/84 (the v1 A3 pA marginal, "
                 "kept for continuity) and 0.875 (the measured EXPLORATORY "
                 "v2 operating marginal, provenance disclosed)",
        "p_pass_ac1_065_at_true_agreement_m0875": {
            "0.679_v1_broken_rate": 0.116,
            "0.729": 0.296,
            "0.75": 0.404,
            "0.80": 0.691,
            "0.85_merely_good_repair": 0.911,
            "0.90": 0.992,
        },
        "p_pass_ac1_065_at_true_agreement_m0690": {
            "0.679_v1_broken_rate": 0.043,
            "0.729": 0.145,
            "0.75": 0.221,
            "0.80": 0.487,
            "0.85_merely_good_repair": 0.790,
            "0.90": 0.967,
        },
        "false_pass_marginal_matched_independent_judges": {
            "at_measured_v2_marginals_0875_0775": 0.300,
            "at_v1_a3_marginals_0690_0631": 0.0011,
            "note": "the retired kappa>=0.40 gate at the v2 marginals: "
                    "independent-pair false-pass 0.0074 but P(pass at true "
                    "agreement 0.85) only 0.700 -- a 30% false-stop on a "
                    "good repair; the kappa gate punishes the rubric for "
                    "raising prevalence (design section 11.1)",
        },
        "burden_shift_note": "at prevalence pi ~ 0.83 ANY pair-agreement "
                             "coefficient discriminates weakly (the between-"
                             "judge signal lives in rare no-items); the "
                             "prevalence-FREE known-answer channels "
                             "(calibration 12/12, deranged <= 0.30, hedge-"
                             "flip <= 2/8 pilot / <= 0.30 full-run) are "
                             "load-bearing instrument evidence on an equal "
                             "footing with AC1 (design section 11.4)",
    },
}
with open(os.path.join(BASE, "pilot-manifest.json"), "w",
          encoding="utf-8") as f:
    f.write(json.dumps(pilot_manifest, indent=1, sort_keys=True) + "\n")

# ---------------- 5. materials/manifest.json (fresh order seeds) ------------
real_ids = sorted(r["id"] for r in items)
probe_ids = {
    arm: sorted(r["id"] for r in load_jsonl(
        os.path.join(V1MAT, "probes-%s.jsonl" % arm)))
    for arm in ("a1", "a2", "a3")}
orders, seeds = {}, {}


def add_block(pk, arm, phase, ids, seed):
    key = "judge-%s|%s|%s" % (pk, arm, phase)
    seeds[key] = seed
    orders[key] = sorted(ids, key=lambda i: sha_str("%s|%s" % (seed, i)))


for pk in ("pA", "pB"):
    for arm in ("a1", "a2", "a3"):
        add_block(pk, arm, "real", real_ids,
                  "ontg2v2/1|judge-%s|%s|real|%s" % (pk, arm, DATE))
        add_block(pk, arm, "probe", probe_ids[arm],
                  "ontg2v2/1|judge-%s|%s|probe|%s" % (pk, arm, DATE))
    for arm in ("a2", "a3"):
        add_block(pk, arm, "hedgeflip", hf_ids[arm],
                  "ontg2v2/1|judge-%s|%s|hedgeflip|%s" % (pk, arm, DATE))
    add_block(pk, "a3", "pilot", pilot_ids,
              "ontg2v2/pilot|judge-%s|a3|%s" % (pk, DATE))
    add_block(pk, "a3", "pilotflip", pilot_flip,
              "ontg2v2/pilotflip|judge-%s|a3|%s" % (pk, DATE))

manifest = {
    "schema": "ontg2v2-materials/1",
    "build_date": DATE,
    "calibration_v1": "poc/g2/materials/calibration-items.jsonl (reused, "
                      "pinned by the harness)",
    "calibration_hedge": "poc/ontology-import-g2-v2/calibration-hedge.jsonl "
                         "(new, pinned by the harness)",
    "n_real": 84, "n_probe_per_arm": 20, "n_hedgeflip_per_hedged_arm": 10,
    "n_pilot": 40, "n_pilot_hedgeflip": 8,
    "order_rule": "sorted(ids, key=sha256(seed|id)) — the "
                  "run-g2lp.py::_run_block rule, fresh v2 seeds",
    "orders": orders,
    "seeds": seeds,
}
with open(os.path.join(BASE, "materials/manifest.json"), "w",
          encoding="utf-8") as f:
    f.write(json.dumps(manifest, indent=1, sort_keys=True) + "\n")

print(json.dumps({
    "prompt-template-v2.txt": file_sha(os.path.join(BASE, "prompt-template-v2.txt")),
    "calibration-hedge.jsonl": file_sha(os.path.join(BASE, "calibration-hedge.jsonl")),
    "probes-hedgeflip-a2.jsonl": file_sha(os.path.join(BASE, "probes-hedgeflip-a2.jsonl")),
    "probes-hedgeflip-a3.jsonl": file_sha(os.path.join(BASE, "probes-hedgeflip-a3.jsonl")),
    "pilot-manifest.json": file_sha(os.path.join(BASE, "pilot-manifest.json")),
    "materials/manifest.json": file_sha(os.path.join(BASE, "materials/manifest.json")),
    "pilot_strata_check": {r: sum(1 for i in pilot_ids
                                  if i in set(by_rule[r][:999]) and
                                  next(x for x in items if x["id"] == i)["rule"] == r)
                           for r in ("R1", "R3", "R4")},
}, indent=1, sort_keys=True))
