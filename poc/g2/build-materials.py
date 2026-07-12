#!/usr/bin/env python3
"""build-materials.py -- g2 PROVISIONAL-ON-LLM-PROXY scoring materials.

Builds the blind judgment items for the g2 stand-in run from the Pi
derived-subsumption dump (poc/g2/pi-derived.jsonl, produced by the
deterministic pi-project.py). One item per judged derived axiom (n = full
dump; the frozen n_planned of 500 is NOT attainable from kernel-v0 -- see
docs/next/analysis/g2-result.md). Rendering is deterministic and BLIND: the
judge sees only the concept's authored label, an everyday-English statement,
and a yes/no/cannot-say question -- never the words kernel/NSM/necessity/
sufficiency/hypothesis (the pinned g3lp blinding list), never URNs, never
derivation provenance.

Probe items (instrument control, NEVER in counts; the house content-scramble
idiom, g3-llmproxy-v3 probe-B / d-adj-t deranged-probe form): 20 seed-pinned
R3 items with the sort target replaced by a wrong sort (Person/Thing/Place ->
Time; Time -> Person), correct answer "no" by construction given the label's
own argument descriptions; measures yes-bias (the channel that would
fabricate high precision). Collisions with true derived axioms are checked
mechanically and logged.

Deterministic: all orders are sha256(seed|id) sorts; no RNG.
"""
import json, os, hashlib, glob

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
G2 = os.path.join(REPO, "poc/g2")
MAT = os.path.join(G2, "materials")
DUMP = os.path.join(G2, "pi-derived.jsonl")

PRIME_NL = {
    "WORDS": "something made of words",
    "SOMEONE": "a person (someone)",
    "SOMETHING~THING": "a thing (something)",
    "PEOPLE": "people",
    "WHEN~TIME": "a time",
    "WHERE~PLACE": "a place",
    "BODY": "a body",
}
SORT_NL = {
    "Thing-sort": "a thing (something — not a person, not a place, not a time)",
    "Person-sort": "a person (someone)",
    "Time-sort": "a time",
    "Place-sort": "a place",
}
DERANGE_SORT = {"Person-sort": "Time-sort", "Thing-sort": "Time-sort",
                "Place-sort": "Time-sort", "Time-sort": "Person-sort"}
# gerund/noun forms for R4 happening-of-kind bodies
EVENT_NOUN = {"break": "breaking", "give": "giving", "lose": "losing",
              "make": "making", "death": "death"}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def word(cid):
    return cid.rsplit(":", 1)[-1].replace("-", " ")


def load_labels():
    out = {}
    for f in sorted(glob.glob(os.path.join(REPO, "data/kernel-v0/concepts/*.json"))):
        o = json.load(open(f, encoding="utf-8"))
        out[o["id"]] = (o["label"], o["explication"]["frame"])
    return out


def rel_vars(label):
    """Extract the two single-capital argument variables from a relational
    label parenthetical, e.g. 'believe (X believes Y)' -> ('X','Y')."""
    import re
    caps = re.findall(r"\b([A-Z])\b", label[label.find("("):] if "(" in label else label)
    if len(caps) >= 2:
        return caps[0], caps[-1]
    return "X", "Y"


def r4_body(a):
    key = (a["pred"], a["role"], a["target_kind"])
    before = "BEFORE" in a["source"]
    other = a.get("det_other", False)
    if key == ("SAY", "agent", "prime"):
        return "there is someone who says the words"
    if key == ("SAY", "addressee", "prime"):
        return ("there is someone else — not the person saying the words "
                "— to whom the words are said")
    if key == ("DO", "agent", "prime"):
        return "there is someone who does something"
    if key == ("DO", "time", "prime"):
        return "there is a time at which the doing happens"
    if key == ("HAPPEN", "time", "prime"):
        return "there is a time at which it happens"
    if key == ("HAPPEN", "undergoer", "concept"):
        noun = EVENT_NOUN[a["target"].rsplit(":", 1)[-1]]
        if before:
            return "at some earlier time, a %s happened" % noun
        return "a %s happens" % noun
    if key == ("HAPPEN", "undergoer", "prime"):
        return "there is something that happens"
    if key == ("BE-SPEC", "undergoer", "prime"):
        if before:
            return "at some earlier time, there was something involved"
        return "there is something involved"
    if key == ("THERE-IS", "undergoer", "prime") and other:
        return ("there is some other thing — distinct from the one "
                "already in view — that exists")
    if key == ("DIE", "undergoer", "prime"):
        return "someone dies"
    if key == ("WANT", "experiencer", "prime") and other:
        return "there is someone else who wants something"
    raise SystemExit("ERR_RENDER: no R4 body for %r" % (a,))


def render(a, labels):
    subj = a["subject"]
    label, frame = labels[subj]
    w = word(subj)
    if a["rule"] == "R1":
        if a["target_kind"] == "prime":
            stmt = "Every %s is %s." % (w, PRIME_NL[a["target"]])
        else:
            stmt = "Every %s is a kind of %s." % (w, word(a["target"]))
    elif a["rule"] == "R3":
        v1, v2 = rel_vars(label)
        v = v1 if a["form"] == "domain" else v2
        stmt = ("In every case of “%s” as described above, "
                "%s is %s." % (label, v, SORT_NL[a["target"]]))
    elif a["rule"] == "R4":
        body = r4_body(a)
        if frame == "InstanceSchema":
            stmt = "In every case of a %s, %s." % (w, body)
        elif frame == "WhenTrue":
            stmt = "Whenever someone or something is %s, %s." % (w, body)
        else:
            stmt = ("In every case of “%s” as described above, %s."
                    % (label, body))
    elif a["rule"] == "R6":
        stmt = ("“%s” holds from a first thing to a second exactly "
                "when “%s” holds from the second to the first."
                % (label, labels[a["target"]][0]))
    else:
        raise SystemExit("ERR_RENDER: rule %r" % a["rule"])
    return "Concept: “%s”\nStatement: %s" % (label, stmt)


PROMPT_TEMPLATE = """You are an independent judge of one-line statements about the meaning of everyday English words. Judge ONLY by the ordinary meaning of the quoted concept (the parenthetical, if any, tells you which sense of the word is meant). Do not use any tools. This is a single standalone question.

{{ITEM}}

Question: Is the statement true as a matter of the concept's ordinary meaning — that is, does it hold in ALL normal cases the concept applies to?
Answer with a single raw JSON object and nothing else — no markdown fence, no prose:
{"answer": "yes"} — true in all normal cases (the concept's meaning guarantees it)
{"answer": "no"} — false, or not guaranteed (there are ordinary cases where it fails, or it misdescribes the concept)
{"answer": "cannot-say"} — only if the statement is genuinely undecidable for this concept
"""

SYSPROMPT_PB = ("You answer with a single raw JSON object of the form "
                "{\"answer\": \"yes\"} or {\"answer\": \"no\"} or "
                "{\"answer\": \"cannot-say\"} and nothing else — no "
                "markdown fence, no prose, no explanation. You never use tools.")

OUTPUT_SCHEMA = {"type": "object",
                 "properties": {"answer": {"type": "string",
                                           "enum": ["yes", "no", "cannot-say"]}},
                 "required": ["answer"], "additionalProperties": False}

CALIBRATION = [
    {"id": "cal:g2-1",
     "item": "Concept: “triangle”\nStatement: Every triangle has "
             "exactly three sides.",
     "expected": "yes"},
    {"id": "cal:g2-2",
     "item": "Concept: “fish”\nStatement: Every fish is a kind of "
             "furniture.",
     "expected": "no"},
]


def main():
    os.makedirs(MAT, exist_ok=True)
    labels = load_labels()
    axioms = [json.loads(l) for l in open(DUMP, encoding="utf-8") if l.strip()]
    judged = [a for a in axioms if a["judged"]]

    items = []
    for a in judged:
        items.append({"id": a["id"], "rule": a["rule"], "form": a["form"],
                      "subject": a["subject"], "item": render(a, labels)})

    # probes: seed-pinned sample of 20 R3 items, sort deranged (see docstring)
    r3 = [a for a in judged if a["rule"] == "R3"]
    seed_sample = "g2lp/1|probe-sample|20260711"
    r3s = sorted(r3, key=lambda a: sha("%s|%s" % (seed_sample, a["id"])))
    true_keys = {(a["subject"], a["form"], a["target"]) for a in judged
                 if a["rule"] == "R3"}
    probes, collisions = [], []
    for a in r3s:
        if len(probes) >= 20:
            break
        wrong = DERANGE_SORT[a["target"]]
        if (a["subject"], a["form"], wrong) in true_keys:
            collisions.append({"probe_source": a["id"], "wrong": wrong,
                               "reason": "collides with a true derived axiom"})
            continue
        b = dict(a, target=wrong)
        probes.append({"id": "g2:probe:%02d" % len(probes),
                       "probe_source": a["id"], "deranged_target": wrong,
                       "item": render(b, labels), "correct": "no"})

    def order_of(seed, ids):
        return sorted(ids, key=lambda i: sha("%s|%s" % (seed, i)))

    ids = [it["id"] for it in items]
    pids = [p["id"] for p in probes]
    manifest = {
        "schema": "g2lp-materials/1",
        "n_items": len(items), "n_probes": len(probes),
        "dump_sha256": hashlib.sha256(open(DUMP, "rb").read()).hexdigest(),
        "seed_real_orders": {"judge-pA": "g2lp/1|judge-pA|20260711",
                             "judge-pB": "g2lp/1|judge-pB|20260711"},
        "seed_probe_orders": {"judge-pA": "g2lp/1|judge-pA-probe|20260711",
                              "judge-pB": "g2lp/1|judge-pB-probe|20260711"},
        "real_orders": {
            "judge-pA": order_of("g2lp/1|judge-pA|20260711", ids),
            "judge-pB": order_of("g2lp/1|judge-pB|20260711", ids)},
        "probe_orders": {
            "judge-pA": order_of("g2lp/1|judge-pA-probe|20260711", pids),
            "judge-pB": order_of("g2lp/1|judge-pB-probe|20260711", pids)},
        "probe_seed_sample": seed_sample,
        "probe_derange_map": DERANGE_SORT,
        "probe_collision_log": collisions,
        "disclosure": ("PROVISIONAL-ON-LLM-PROXY g2 materials; n_items is the "
                       "FULL Pi dump over kernel-v0 (the frozen n_planned=500 "
                       "is unattainable from the pinned corpus)."),
    }

    def wjsonl(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    wjsonl(os.path.join(MAT, "items.jsonl"), items)
    wjsonl(os.path.join(MAT, "probes.jsonl"), probes)
    wjsonl(os.path.join(MAT, "calibration-items.jsonl"), CALIBRATION)
    open(os.path.join(MAT, "prompt-template.txt"), "w", encoding="utf-8").write(PROMPT_TEMPLATE)
    open(os.path.join(MAT, "judge-pB-system-prompt.txt"), "w", encoding="utf-8").write(SYSPROMPT_PB + "\n")
    with open(os.path.join(MAT, "output-schema.json"), "w") as f:
        f.write(json.dumps(OUTPUT_SCHEMA, indent=1, sort_keys=True) + "\n")
    with open(os.path.join(MAT, "manifest.json"), "w") as f:
        f.write(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    # blinding self-check over every judge-VISIBLE byte (pinned token list).
    # Note: item metadata (subject URNs etc.) never reaches a judge; the
    # runner assembles user prompts from the "item" text alone and re-scans
    # each assembled prompt with the pinned g3lp blinding_scan at call time.
    banned = (b"kernel", b"nsm", b"necessity", b"sufficiency", b"hypothesis")
    visible = ([it["item"] for it in items] + [p["item"] for p in probes]
               + [c["item"] for c in CALIBRATION]
               + [PROMPT_TEMPLATE, SYSPROMPT_PB])
    for i, txt in enumerate(visible):
        blob = txt.encode("utf-8").lower()
        for t in banned:
            if t in blob:
                raise SystemExit("ERR_BLIND: %r in visible text #%d: %r"
                                 % (t, i, txt[:120]))
    print(json.dumps({"n_items": len(items), "n_probes": len(probes),
                      "collisions": len(collisions),
                      "materials_sha": {fn: hashlib.sha256(open(os.path.join(MAT, fn), "rb").read()).hexdigest()
                                        for fn in sorted(os.listdir(MAT))}},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
