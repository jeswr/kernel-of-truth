#!/usr/bin/env python3
"""resolve_judge3 -- MECHANICAL application of the issue-#9 maintainer resolution
rule to the 36 discordant f2b-transfer stage-1 adjudication items.

Maintainer rule (issue #9, @jeswr): run judge-3 (GPT-5.6) on the 36 discordant
items; RESOLVE a discordant item to the HUMAN's (judge-1) label ONLY where
judge-3 agrees with the human; leave the rest UNRESOLVED and LIST them.

Opus experiment-runner EXECUTION role: DESIGNS NOTHING, CONCLUDES NOTHING. Every
definition below traces to the FROZEN assembler
(poc/f2b-transfer/llmproxy-runs/20260710T001512Z/assemble-llmproxy.py) and the
analysis harness (analysis/f2b_transfer.py). Fail closed on any mismatch.

VALIDATION GATE: reproduce the committed stage-1 integers from the raw judge-1
(human) + judge-2 + membership-gold files BEFORE folding in judge-3. If the
reproduction does not match stage1-analysis.json (n_agree=317, resolved=324,
discordant=36), ABORT -- do not emit a resolution.
"""
import json, os, sys, hashlib

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
sys.path.insert(0, REPO)
from analysis.f2b_transfer import wilson_lb  # exact LB used by the frozen harness

J1  = os.path.join(REPO, "poc/f2b-transfer/judge-1-results/judge-1-responses.jsonl")  # HUMAN
J2  = os.path.join(REPO, "data/d-adj-t/judge-2-responses.jsonl")
J3  = os.path.join(REPO, "poc/f2b-transfer/judge-1-results/judge-3-responses.jsonl")  # GPT-5.6
GOLD = os.path.join(REPO, "data/d-qa-t/items/covered.jsonl")
STAGE1 = os.path.join(REPO, "poc/f2b-transfer/judge-1-results/stage1-analysis.json")

ESCAPE_TOKENS = {"NONE", "cannot say"}


def die(msg):
    sys.stderr.write("RESOLVE_JUDGE3_ABORT: %s\n" % msg)
    sys.exit(2)


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    gold = {r["id"]: r["answer"] for r in load(GOLD)}
    j1 = {r["id"]: r["answer"] for r in load(J1)}
    j2 = {r["id"]: r["answer"] for r in load(J2)}
    j3 = {r["id"]: r["answer"] for r in load(J3)}
    stage1 = json.load(open(STAGE1))

    ids = sorted(j1.keys())
    if len(ids) != 360:
        die("expected 360 human judge-1 items, got %d" % len(ids))
    for iid in ids:
        if iid not in gold: die("id missing membership gold: %s" % iid)
        if iid not in j2:   die("id missing judge-2: %s" % iid)

    # ---- STAGE-1 REPRODUCTION (validation gate) --------------------------------
    # resolved (n_ext_labelled) = concordant both-labelled byte-equal pairs.
    # The stage-1 "n_unresolved_disagreement" bucket = 360 - resolved, which
    # lumps discordant pairs (a1!=a2) with any not-both-labelled item; that whole
    # NON-RESOLVED set is exactly what judge-3 was run on.
    resolved_ids = set()
    agree = 0
    disc_pairs = 0
    for iid in ids:
        g, a1, a2 = gold[iid], j1[iid], j2[iid]
        both = (a1 is not None) and (a2 is not None)
        if both and a1 == a2:               # concordant = resolved (byte-equal)
            resolved_ids.add(iid)
            if a1 == g:                     # shared token vs membership gold
                agree += 1
        elif both:
            disc_pairs += 1
    resolved = len(resolved_ids)
    nonresolved_ids = set(ids) - resolved_ids       # 36 = judge-3 set

    exp_agree = int(stage1["adj"]["n_agree_membership"])       # 317
    exp_resolved = int(stage1["adj"]["n_ext_labelled"])        # 324
    exp_unres = int(stage1["adj"]["n_unresolved_disagreement"])# 36
    if (agree, resolved, len(nonresolved_ids)) != (exp_agree, exp_resolved, exp_unres):
        die("stage-1 reproduction MISMATCH: got agree=%d resolved=%d nonres=%d; "
            "expected %d/%d/%d" % (agree, resolved, len(nonresolved_ids),
                                   exp_agree, exp_resolved, exp_unres))
    if set(j3.keys()) != nonresolved_ids:
        die("judge-3 ids != non-resolved set (j3=%d, nonres=%d, sym-diff=%d)"
            % (len(j3), len(nonresolved_ids), len(set(j3) ^ nonresolved_ids)))
    sys.stderr.write("VALIDATION GATE PASS: reproduced stage-1 agree=%d "
                     "resolved=%d non-resolved=%d (of which %d discordant pairs, "
                     "%d not-both-labelled); judge-3 set matches\n"
                     % (agree, resolved, len(nonresolved_ids), disc_pairs,
                        len(nonresolved_ids) - disc_pairs))

    # ---- APPLY MAINTAINER RULE (over the 36 non-resolved / judge-3 items) -------
    newly_resolved = []   # (id, human_label, gold, agree_membership)
    unresolved = []       # (id, human_j1, j2, judge3, gold)
    for iid in sorted(nonresolved_ids):
        g, a1, a2, a3 = gold[iid], j1[iid], j2[iid], j3[iid]
        # "resolve to the HUMAN's label ONLY where GPT-5.6 agrees with the human":
        # requires a non-null human label AND judge-3 token-equal to it.
        if a1 is not None and a3 is not None and a3 == a1:
            newly_resolved.append((iid, a1, g, a1 == g))
        else:
            unresolved.append({"id": iid, "human_judge1": a1, "judge2": a2,
                               "judge3_gpt56": a3, "membership_gold": g})
    n_disc = len(nonresolved_ids)

    R = len(newly_resolved)
    add_agree = sum(1 for (_, _, _, am) in newly_resolved if am)

    n_ext_new = resolved + R
    n_agree_new = agree + add_agree
    n_unres_new = n_disc - R
    A_new = n_agree_new / n_ext_new if n_ext_new else 0.0
    A_lb_new = wilson_lb(A_new, n_ext_new)

    out = {
        "rule": "issue-#9: resolve discordant to HUMAN(judge-1) label iff "
                "judge-3(GPT-5.6)==judge-1; else UNRESOLVED",
        "stage1_prior": {"n_agree_membership": agree, "n_ext_labelled": resolved,
                         "n_unresolved": n_disc,
                         "A": agree / resolved, "A_lb": wilson_lb(agree / resolved, resolved)},
        "judge3_resolution": {
            "n_discordant": n_disc,
            "n_newly_resolved": R,
            "n_newly_resolved_agree_membership": add_agree,
            "n_still_unresolved": n_unres_new},
        "stage1_post_judge3": {
            "n_agree_membership": n_agree_new, "n_ext_labelled": n_ext_new,
            "n_unresolved": n_unres_new, "n_adjudicated": 360,
            "external_endorsement": A_new, "external_endorsement_lb": A_lb_new,
            "endorsement_bar": 0.70,
            "stage1_endorsement_fail": A_lb_new < 0.70},
        "unresolved_items": unresolved,
        "newly_resolved_ids": [nr[0] for nr in newly_resolved],
    }
    outpath = os.path.join(REPO, "poc/f2b-transfer/judge-1-results/judge-3-resolution.json")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("stage1_prior", "judge3_resolution", "stage1_post_judge3")},
                     indent=2))
    sys.stderr.write("RESOLVE_DONE R=%d add_agree=%d A=%.6f LB=%.6f still_unresolved=%d\n"
                     % (R, add_agree, A_new, A_lb_new, n_unres_new))


if __name__ == "__main__":
    main()
