#!/usr/bin/env python3
"""assemble_d_adj_t -- MECHANICAL assembler of the d-adj-t blind-adjudication-labels
corpus (data/d-adj-t/) per FROZEN design.md §3.2, applying the maintainer-confirmed
issue-#9 resolution rule (judge-3 resolves toward the human ONLY where they agree).

Writes into data/d-adj-t/ (which already holds the judge-2 protocol files):
  - labels.jsonl   one line per item {id, gold_ext|null, undecided, unresolved, votes}
  - summary.json   the exact counts the stage-1 adjudication-instrument record carries
  - PROTOCOL.md     verbatim copy of design.md §4 (the pinned adjudication protocol)
  - judge-1-responses.jsonl / judge-3-responses.jsonl  (pseudonymous raw votes; RT-14)

Opus experiment-runner EXECUTION role: DESIGNS NOTHING, CONCLUDES NOTHING. Reuses the
VALIDATED resolution in judge-3-resolution.json (which passed the stage-1 reproduction
gate). Fail-closed on any mismatch. Does NOT pin, ops-amend, or log (coordinator steps).
"""
import json, os, sys, re, shutil, hashlib

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
JR = os.path.join(REPO, "poc/f2b-transfer/judge-1-results")
D = os.path.join(REPO, "data/d-adj-t")
ESCAPE = {"NONE", "cannot say", "cannot-say"}


def die(m):
    sys.stderr.write("ASSEMBLE_DADJT_ABORT: %s\n" % m); sys.exit(2)


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    gold = {r["id"]: r["answer"] for r in load(os.path.join(REPO, "data/d-qa-t/items/covered.jsonl"))}
    j1 = {r["id"]: r["answer"] for r in load(os.path.join(JR, "judge-1-responses.jsonl"))}
    j2 = {r["id"]: r["answer"] for r in load(os.path.join(REPO, "data/d-adj-t/judge-2-responses.jsonl"))}
    j3 = {r["id"]: r["answer"] for r in load(os.path.join(JR, "judge-3-responses.jsonl"))}
    res = json.load(open(os.path.join(JR, "judge-3-resolution.json")))
    newly = set(res["newly_resolved_ids"])
    unresolved_ids = {u["id"] for u in res["unresolved_items"]}

    ids = sorted(j1.keys())
    rows = []
    n_agree = n_ext = n_unres = n_undecided = 0
    jp_total = jp_conc = 0
    for iid in ids:
        g, a1, a2 = gold[iid], j1[iid], j2.get(iid)
        both = (a1 is not None) and (a2 is not None)
        if both:
            jp_total += 1
        votes = {"judge-1": a1, "judge-2": a2}
        gold_ext = None
        undecided = False
        unresolved = False
        if both and a1 == a2:                      # concordant pair -> resolved
            jp_conc += 1
            gold_ext = a1
            undecided = a1 in ESCAPE               # concordant escape => undecided
            n_ext += 1
            if a1 == g and not undecided:
                n_agree += 1
            if undecided:
                n_undecided += 1
        else:                                       # non-resolved -> judge-3 ran
            votes["judge-3"] = j3.get(iid)
            if iid in newly:                        # #9 rule: j3==human -> human label
                gold_ext = a1
                n_ext += 1
                if a1 == g:
                    n_agree += 1
            else:                                   # unresolved (incl. human abstain)
                unresolved = True
                n_unres += 1
        rows.append({"id": iid, "gold_ext": gold_ext, "undecided": undecided,
                     "unresolved": unresolved, "votes": votes})

    # cross-check against the validated resolution artifact
    post = res["stage1_post_judge3"]
    if (n_agree, n_ext, n_unres) != (post["n_agree_membership"], post["n_ext_labelled"], post["n_unresolved"]):
        die("metric mismatch vs judge-3-resolution.json: got agree=%d ext=%d unres=%d; "
            "expected %d/%d/%d" % (n_agree, n_ext, n_unres, post["n_agree_membership"],
                                   post["n_ext_labelled"], post["n_unresolved"]))
    if len(unresolved_ids) != n_unres:
        die("unresolved set size mismatch: labels=%d resolution=%d" % (n_unres, len(unresolved_ids)))

    # ---- write labels.jsonl (sorted by id) ----
    lp = os.path.join(D, "labels.jsonl")
    with open(lp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    # ---- PROTOCOL.md: verbatim §4 of design.md ----
    dm = open(os.path.join(REPO, "poc/f2b-transfer/design.md"), encoding="utf-8").read()
    m = re.search(r"(^## 4\. Adjudication protocol.*?)(?=^## 5\.)", dm, re.S | re.M)
    if not m:
        die("could not extract §4 from design.md for PROTOCOL.md")
    with open(os.path.join(D, "PROTOCOL.md"), "w", encoding="utf-8") as f:
        f.write("<!-- verbatim copy of poc/f2b-transfer/design.md §4 (adjudication protocol); "
                "d-adj-t §3.2 requirement. -->\n\n" + m.group(1).rstrip() + "\n")

    # ---- copy pseudonymous raw judge votes into the corpus (RT-14: no PII) ----
    for src in ("judge-1-responses.jsonl", "judge-3-responses.jsonl"):
        shutil.copyfile(os.path.join(JR, src), os.path.join(D, src))

    # ---- summary.json: the stage-1 record's exact integers ----
    summary = {
        "experiment": "f2b-transfer", "arm": "adjudication-instrument",
        "resolution_rule": res["rule"],
        "analysis_input_metrics": {
            "n_adjudicated": 360, "n_unresolved_disagreement": n_unres,
            "n_undecided": n_undecided, "n_agree_membership": n_agree,
            "judge_pairs_total": jp_total, "judge_pairs_concordant": jp_conc,
            "n_ext_labelled": n_ext, "n_eval_items": 250,
            "labels_sha256": hashlib.sha256(open(lp, "rb").read()).hexdigest()},
        "external_endorsement": post["external_endorsement"],
        "external_endorsement_lb": post["external_endorsement_lb"],
        "sourcing_disclosure": {
            "judge_1": {"role": "human, kernel-naive (SOLE gold source)", "pseudonym": "judge-1"},
            "judge_2": {"role": "blind LLM judge (gpt-5.6-sol, codex 0.144.1, effort low)", "pseudonym": "judge-2"},
            "judge_3": {"role": "tie-break on discordant (gpt-5.6-sol); issue-#9 rule resolves "
                        "toward the human ONLY where judge-3==human; judge-2 and judge-3 are ONE "
                        "model family, so judge-3 is a conservative human-confirmation step, NOT "
                        "independent validation", "pseudonym": "judge-3"},
            "membership_gold": {"source": "data/d-qa-t/items/covered.jsonl", "corpus": "d-qa-t",
                                "pin": "7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27"}},
    }
    with open(os.path.join(D, "summary.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

    print(json.dumps(summary["analysis_input_metrics"], sort_keys=True))
    sys.stderr.write("ASSEMBLE_DADJT_DONE agree=%d ext=%d unres=%d undecided=%d jp=%d/%d\n"
                     % (n_agree, n_ext, n_unres, n_undecided, jp_conc, jp_total))


if __name__ == "__main__":
    main()
