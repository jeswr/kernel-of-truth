#!/usr/bin/env python3
"""build-materials.py -- Stage-A V-A + V-B materials build (sense-split-first
construction, docs/next/design/sense-split-first-construction.md section 5;
Stage A scope ASM-1909; assumption block data/kernel-v1/asm-stageA-*.json).

Generates, from the BUILT kernel-v1 Stage-A corpus (data/kernel-v1/) and its
per-sense soft-type records:

  materials/va-items.jsonl       30 sense-scoped soft-type renders (V-A): the
                                 five g2 sense-channel items 011/036/037/070/
                                 071 + the friend 040/041 latent pair,
                                 re-rendered per sense with a REAL sense gloss
                                 in the parenthetical (v2.2 template idiom)
  materials/vb-items.jsonl       31 binding referent-sort renders (V-B): every
                                 hard SomeoneRef/SomethingRef/TimeRef/PlaceRef
                                 commitment inside the 11 explications, as a
                                 per-sense ordinary-meaning claim -- the
                                 sense-scoped successor of the word-scoped
                                 0.3929 (ASM-1881/1887)
  materials/resolution-map.json  pre-stated V-A resolution criterion per g2
                                 item (readout expectation, NOT a gate:
                                 >=4/5 resolve, ASM-1907)
  materials/manifest.json        sha-pins of every consumed input, per-judge
                                 per-phase order seeds, call/budget plan

$0: no LLM calls. Deterministic: same inputs -> same bytes.
"""
import json, hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
KV1 = os.path.join(REPO, "data", "kernel-v1")
MAT = os.path.join(HERE, "materials")

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def die(m):
    sys.stderr.write("BUILD_MATERIALS_ABORT: %s\n" % m); sys.exit(2)

# ---- consumed inputs (pinned into the manifest) ----
INPUTS = [
    "data/kernel-v1/manifest.json",
    "data/kernel-v1/minted-urns.jsonl",
    "data/kernel-v1/typing/soft-type-per-sense.jsonl",
    "data/kernel-v1/typing/ck-ufo-sidecar.jsonl",
    "poc/ontology-import-g2-v2/prompt-template-v2.2.txt",
    "poc/ontology-import-g2-v2/calibration-hedge-v22.jsonl",
    "poc/g2/materials/calibration-items.jsonl",
    "poc/g2/materials/judge-pB-system-prompt.txt",
    "poc/g2/materials/output-schema.json",
] + sorted(
    "data/kernel-v1/concepts/" + f for f in os.listdir(os.path.join(KV1, "concepts"))
)

manifest_kv1 = json.load(open(os.path.join(KV1, "manifest.json")))
if manifest_kv1["gates"]["G1_duplicateIdentityGroups"] != 0:
    die("kernel-v1 G1 not clean")
concepts = {}
for c in manifest_kv1["concepts"]:
    rec = json.load(open(os.path.join(KV1, c["file"])))
    concepts[rec["id"]] = rec

soft = [json.loads(l) for l in open(os.path.join(KV1, "typing/soft-type-per-sense.jsonl")) if l.strip()]
if len(soft) != 30:
    die("expected 30 per-sense soft-type records, got %d" % len(soft))

def concept_line(cid):
    return "Concept: “%s”" % concepts[cid]["label"]

# ---- V-A statement curation table (sense, form) -> statement ----------------
# v2.2 idiom: unhedged sentences claim ALL normal cases; Normally/Typically
# sentences claim the usual case (prompt-template-v2.2.txt sentence-force rules).
VA = {
 ("break.shatter","domain"): "In every case of “break.shatter” as described above, X is what does the breaking — someone or something whose doing makes Y come apart; not a time and not a place. Normally X is a person, but it can as well be a thing or a happening — a storm, a falling rock, a blow. Typically X acts on Y by force.",
 ("break.shatter","range"): "In every case of “break.shatter” as described above, Y is a thing that can be in one piece and then not — something with a body or material to it, not a time and not a bare idea. Normally Y is a whole object — one thing that comes apart or stops holding together. Typically the breaking leaves pieces.",
 ("break.shatter","existential"): "In every case of “break.shatter” as described above, the breaking happens at some time — there is a time at which it takes place. Normally one can say when it happened, at least roughly.",
 ("break.shatter-become","domain"): "In every case of “break.shatter-become” as described above, Y — the thing that breaks — is something with a body or material to it, a thing that can be in one piece and then in many pieces; not a time and not a bare idea. Normally Y is a whole object. Typically the breaking leaves pieces.",
 ("break.shatter-become","existential"): "In every case of “break.shatter-become” as described above, the breaking happens at some time — there is a time at which it takes place. Normally one can say when it happened, at least roughly.",
 ("break.malfunction","domain"): "In every case of “break.malfunction” as described above, X is the one whose doing leaves Y not working — someone, or something that acts; not a time and not a place. Normally X is a person doing something to Y. Typically X does something to Y — takes it apart, drops it, mishandles it.",
 ("break.malfunction","range"): "In every case of “break.malfunction” as described above, Y is a thing that can work and then not work — a thing with a body or material to it that is for doing something, like a clock, a machine, or a tool. Normally Y stays in one piece — it is not shattered, it just no longer does what it is for.",
 ("break.malfunction","existential"): "In every case of “break.malfunction” as described above, the breaking happens at some time — there is a time at which Y stops working as it should. Normally one can say when it happened, at least roughly.",
 ("break.violate","domain"): "In every case of “break.violate” as described above, X is the one who does not do what the words say — a someone: a person, or people; not a mere thing, not a time, not a place. Normally X could have done otherwise. Typically people can think something bad about X because of it.",
 ("break.violate","range"): "In every case of “break.violate” as described above, Y is something made of words — a promise, a law, a rule, an agreement; not a material thing with a body to it. Normally Y says what people must do or must not do. Typically Y still stands for others after X breaks it.",
 ("break.violate","existential"): "In every case of “break.violate” as described above, the breaking happens at some time — there is a time at which X does the thing the words say cannot be done. Normally one can say when it happened, at least roughly.",
 ("break.interrupt","domain"): "In every case of “break.interrupt” as described above, X is what makes the continuing thing stop — someone or something whose doing stops it; not a time and not a place. Normally X is a person or a happening. Typically X does something at a moment, and the continuing thing stops then.",
 ("break.interrupt","range"): "In every case of “break.interrupt” as described above, Y is a continuing something — a happening that has been going on, like a silence, a streak, a cycle, a habit; not a material object one can hold. Normally Y was going on for some time before. Typically after the breaking Y is no longer going on.",
 ("break.interrupt","existential"): "In every case of “break.interrupt” as described above, the breaking happens at some time — there is a time at which the continuing thing stops. Normally one can say when it happened, at least roughly.",
 ("make.create","domain"): "In every case of “make.create” as described above, X is the maker — the one whose doing brings Y into being; not a time and not a place. Normally X is a person, or people working together. Typically X shapes things or puts things together.",
 ("make.create","range"): "In every case of “make.create” as described above, Y is what is made — something that comes to be through the making and was not there before. Normally Y is a thing one can point to afterwards — an object, a stuff, a work, like a chair, a cake, a wall. Typically Y is made out of other things.",
 ("make.create","existential"): "In every case of “make.create” as described above, the making happens at some time — there is a time at which it takes place. Normally one can say when it happened, at least roughly.",
 ("make.cause","domain"): "In every case of “make.cause” as described above, X is the one who gets Y to do something — a someone who wants Y to do it and does something so that Y does; not a time and not a place. Normally X is a person, or people. Typically Y would not have done it without X.",
 ("make.cause","range"): "In every case of “make.cause” as described above, Y is the one who is made to do something — a someone: a person, or people; not a mere thing, not a time, not a place. Normally Y does the thing after what X does. Typically Y does it because of X.",
 ("make.cause","existential"): "In every case of “make.cause” as described above, the making-happen happens at some time — there is a time at which X does what gets Y to act. Normally one can say when it happened, at least roughly.",
 ("find.locate","domain"): "In every case of “find.locate” as described above, X is the one that does the finding — someone or something that can look for things or come upon them; not a time or a place. Normally X is a person, or an animal or other being that can perceive. Typically X was looking for Y, or at least comes to know where Y is.",
 ("find.locate","range"): "In every case of “find.locate” as described above, Y is what is found — something that was somewhere all along, not known to X to be there, and then is seen. Normally Y is a thing one can see — an object, a person, an animal, a place. Typically Y was missed or lost before.",
 ("find.locate","existential"): "In every case of “find.locate” as described above, the finding fixes a place — there is a place where Y is, and X comes to know it. Normally one can say where Y was found.",
 ("find.discover","domain"): "In every case of “find.discover” as described above, X is the one who comes to know — a someone who can think and know things; not a time and not a place. Normally X is a person. Typically X was looking into something, or thinking about it.",
 ("find.discover","range"): "In every case of “find.discover” as described above, Y is what is found out — something that comes to be known, like a flaw, an answer, or that something is so; not a material thing one can hold. Normally Y was so before X knew it. Typically X can say Y in words afterwards.",
 ("find.discover","existential"): "In every case of “find.discover” as described above, the finding-out happens at some time — there is a time at which X comes to know Y. Normally one can say when it happened, at least roughly.",
 ("friend.person","domain"): "In every case of “friend.person” as described above, X is a person — a someone one can know well and feel affection and trust toward; not a mere thing, not a time, not a place. Normally X is one of two people who like each other and are close. Typically X and Y do things together and feel something good.",
 ("friend.person","range"): "In every case of “friend.person” as described above, Y is a person — a someone who knows X well and regards X with affection and trust; not a mere thing, not a time, not a place. Normally Y is one of two people who like each other and are close.",
 ("friend.figurative","domain"): "In every case of “friend.figurative” as described above, X — the friend — is not a person: it is a something that a person thinks about the way one thinks about a friend, like an imaginary friend, a beloved toy, or an animal companion. Normally X is something the person knows well and feels something good about. Typically the person speaks of X as a friend.",
 ("friend.figurative","range"): "In every case of “friend.figurative” as described above, Y is the one who has the friend — a someone: a person; not a mere thing, not a time, not a place. Normally Y feels something good when doing things with X. Typically Y speaks of X as a friend.",
}

# ---- V-B referent-sort claim table: (sense, ref index) -> (sort, claim) -----
VB = {
 ("break.shatter",1): ("SomethingRef","X — what does the breaking — is a something: anything whose doing can make Y come apart. It need not be a person: a storm or a falling rock can break a window. Normally it is a person or a moving thing."),
 ("break.shatter",2): ("SomethingRef","Y — what gets broken — is a something: a thing, not a time and not a place; the thing that comes apart into pieces."),
 ("break.shatter",3): ("TimeRef","the breaking takes place at some time — there is a time such that before it Y was one thing and after it Y is in pieces. Normally one can say when."),
 ("break.shatter-become",1): ("SomethingRef","Y — the thing that breaks — is a something: a thing, not a time and not a place; the thing that comes apart into pieces."),
 ("break.shatter-become",2): ("TimeRef","the breaking takes place at some time — there is a time such that before it Y was one thing and after it Y is in pieces. Normally one can say when."),
 ("break.malfunction",1): ("SomeoneRef","X — the one who breaks Y — is a someone: a person, or people. (On this reading, if a power surge rather than anyone's doing stops the clock, this concept does not apply.) Normally X did something to Y."),
 ("break.malfunction",2): ("SomethingRef","Y — what is broken — is a something: a thing, like a clock, a machine, or a tool; not a person and not a time."),
 ("break.malfunction",3): ("TimeRef","the breaking takes place at some time — there is a time after which Y no longer works as it should. Normally one can say when."),
 ("break.violate",1): ("SomeoneRef","X — the one who breaks the promise, the law, or the rule — is a someone: a person, or people. A storm cannot break a promise."),
 ("break.violate",2): ("SomethingRef","Y — what is broken — is a something: the words (a promise, a law, a rule); not a person and not a time."),
 ("break.violate",3): ("SomethingRef","the thing done — what the words say cannot be done — is a something: a doable something; not a person, not a time, not a place."),
 ("break.violate",4): ("TimeRef","the breaking takes place at some time — there is a time at which X does what the words say cannot be done. Normally one can say when."),
 ("break.interrupt",1): ("SomethingRef","X — what breaks the continuing thing — is a something: a person, a thing, or a happening; it need not be a person."),
 ("break.interrupt",2): ("SomethingRef","Y — what is broken — is a something: a continuing happening (a silence, a streak, a cycle); not a person, and not a material object one can hold."),
 ("break.interrupt",3): ("TimeRef","the breaking takes place at some time — there is a time at which the continuing thing stops. Normally one can say when."),
 ("make.create",1): ("SomeoneRef","X — the maker — is a someone: a person, or people. (On this reading, if no one made it, nothing was ‘made’.)"),
 ("make.create",2): ("SomethingRef","Y — what is made — is a something: a thing that comes to exist; not a time and not a place."),
 ("make.create",3): ("TimeRef","the making takes place at some time — there is a time before which Y was not and after which Y is. Normally one can say when."),
 ("make.cause",1): ("SomeoneRef","X — the one who makes Y do something — is a someone: a person, or people."),
 ("make.cause",2): ("SomeoneRef","Y — the one made to do something — is a someone: a person, or people. A stone cannot be made to apologize."),
 ("make.cause",3): ("TimeRef","the making-happen takes place at some time — there is a time at which X does what gets Y to act. Normally one can say when."),
 ("find.locate",1): ("SomeoneRef","X — the finder — is a someone: a person, or another being that can see and come to know. (On this reading a metal detector does not itself ‘find’ — the someone using it does.)"),
 ("find.locate",2): ("SomethingRef","Y — what is found — is a something: a thing that is somewhere and can be seen; not a time."),
 ("find.locate",3): ("PlaceRef","there is a place — the place where Y is; the finding fixes it, and X comes to know it."),
 ("find.discover",1): ("SomeoneRef","X — the one who finds out — is a someone: a person, or people."),
 ("find.discover",2): ("SomethingRef","Y — what is found out — is a something: a flaw, an answer, a fact; not a time and not a place."),
 ("find.discover",3): ("TimeRef","the finding-out takes place at some time — there is a time at which X comes to know Y. Normally one can say when."),
 ("friend.person",1): ("SomeoneRef","X — the friend — is a someone: a person. On this reading a toy or an app is not a friend — that way of speaking belongs to the figurative sense."),
 ("friend.person",2): ("SomeoneRef","Y — the one whose friend X is — is a someone: a person."),
 ("friend.figurative",1): ("SomethingRef","X — the friend — is a something: it need not be a person; an imaginary friend, a beloved toy, or an animal companion can fill it."),
 ("friend.figurative",2): ("SomeoneRef","Y — the one who has the friend — is a someone: a person, or people."),
}

# ---- consistency gates against the built corpus -----------------------------
soft_keys = {(r["concept"].replace("urn:kernel-v1:",""), r["position"]["form"]) for r in soft}
if soft_keys != set(VA.keys()):
    die("VA table keys != soft-type records: only=%s missing=%s"
        % (sorted(set(VA) - soft_keys), sorted(soft_keys - set(VA))))
for (sense, idx), (sort, _) in sorted(VB.items()):
    cid = "urn:kernel-v1:" + sense
    refs = {r["index"]: r["refKind"] for r in concepts[cid]["explication"]["referents"]}
    if refs.get(idx) != sort:
        die("VB sort mismatch %s ref%d: explication says %s, table says %s"
            % (sense, idx, refs.get(idx), sort))
vb_expected = sum(len(c["explication"]["referents"]) for c in concepts.values())
if len(VB) != vb_expected:
    die("VB covers %d referents, explications declare %d" % (len(VB), vb_expected))

# ---- emit items --------------------------------------------------------------
os.makedirs(MAT, exist_ok=True)
va_rows = []
for r in sorted(soft, key=lambda r: r["id"]):
    sense = r["concept"].replace("urn:kernel-v1:", "")
    form = r["position"]["form"]
    va_rows.append({
        "id": "ssA:va:%s:%s" % (sense, form),
        "kind": "V-A per-sense soft-type render",
        "subject": r["concept"], "softTypeRecord": r["id"], "form": form,
        "item": "%s\nStatement: %s" % (concept_line(r["concept"]), VA[(sense, form)]),
    })
vb_rows = []
for (sense, idx) in sorted(VB):
    sort, claim = VB[(sense, idx)]
    cid = "urn:kernel-v1:" + sense
    vb_rows.append({
        "id": "ssA:vb:%s:ref%d" % (sense, idx),
        "kind": "V-B binding referent-sort claim",
        "subject": cid, "refIndex": idx, "refKind": sort,
        "item": "%s\nStatement: In every case of “%s” as described above, %s"
                % (concept_line(cid), sense, claim),
    })
with open(os.path.join(MAT, "va-items.jsonl"), "w") as f:
    for r in va_rows: f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
with open(os.path.join(MAT, "vb-items.jsonl"), "w") as f:
    for r in vb_rows: f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

# ---- resolution map (pre-stated readout expectation, NOT a gate) -------------
res = {
 "criterion": "a g2 sense-channel item RESOLVES iff every V-A item listed for it receives a decisive (yes/no) pA==pB verdict AND the per-sense verdict pattern is coherent with the sense record (no new sense-channel disagreement on split items). Pre-stated expectation, not a gate: >=4/5 of the numbered items resolve (ASM-1907 / design section 5 V-A). Falsifier: persistent disagreement on sense-split items = instrument or typing-content defect, a genuine correctness signal.",
 "items": {
  "g2:pi:011": {"va": ["ssA:va:break.shatter:range", "ssA:va:break.violate:range"],
                "absence_check": "the word-scoped defect record (break range -> material entity at word scope) is UNMINTABLE against kernel-v1: build gate ERR_PI011_CLASS_REMINT forbids any break.violate range record anchored at BFO_0000040 (PASS at corpus build)"},
  "g2:pi:036": {"va": ["ssA:va:find.locate:domain", "ssA:va:find.discover:domain"]},
  "g2:pi:037": {"va": ["ssA:va:find.locate:range", "ssA:va:find.discover:range"]},
  "g2:pi:070": {"va": ["ssA:va:make.create:range", "ssA:va:make.cause:range"]},
  "g2:pi:071": {"va": ["ssA:va:make.create:existential", "ssA:va:make.cause:existential"]}
 },
 "latent_pair": {
  "g2:pi:040+g2:pi:041 (friend)": {"va": ["ssA:va:friend.person:domain", "ssA:va:friend.person:range",
                                            "ssA:va:friend.figurative:domain", "ssA:va:friend.figurative:range"],
                                     "note": "adjudication B.iii latent sibling; reported alongside the 5, outside the >=4/5 expectation"}
 },
 "vb_measure": "sense-scoped soundness of the binding referent sorts = fraction of the 31 V-B items judged sound (both-decisive both-yes) with a Wilson 95% CI; this is the first well-posed estimate of hard-typing soundness and REPLACES 0.3929 as the quantity of record; 0.3929 stands re-labelled a word-scoped lower bound (design section 5 V-B, ASM-1887)."
}
with open(os.path.join(MAT, "resolution-map.json"), "w") as f:
    f.write(json.dumps(res, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

# ---- order seeds (fresh per judge per phase, v2 convention) ------------------
def order_for(seed, ids):
    return sorted(ids, key=lambda i: hashlib.sha256(("%s|%s" % (seed, i)).encode()).hexdigest())

orders, seeds = {}, {}
for pk in ("pA", "pB"):
    for phase, rows in (("va", va_rows), ("vb", vb_rows)):
        key = "judge-%s|%s" % (pk, phase)
        seed = "ssA/%s|judge-%s|2026-07-12" % (phase, pk)
        seeds[key] = seed
        orders[key] = order_for(seed, [r["id"] for r in rows])

# ---- cost plan ---------------------------------------------------------------
CAL_PER_JUDGE = 10          # 2 v1 calibration + 8 v2.2 hedge calibration
calls = 2 * (CAL_PER_JUDGE + len(va_rows) + len(vb_rows))
PRICE_BOUND = 0.012         # pinned conservative bound, carried from ontg2v2 (ASM-1874/1906)
CEILING = 200               # hard call ceiling incl. content-retry headroom
plan = {
 "expected_calls": calls,
 "expected_usd_at_price_bound": round(calls * PRICE_BOUND, 3),
 "hard_call_ceiling": CEILING,
 "worst_case_usd_bound": round(CEILING * PRICE_BOUND, 3),
 "usd_cap": 10.0,
 "price_bound_usd_per_call": PRICE_BOUND,
 "design_band": "<= $10 model spend (design section 6.1 Stage A); measured v2.2 anchors ~$0.008-0.012/judgment (ASM-1906)",
}

manifest = {
 "schema": "ssA-materials/1",
 "build_date": "2026-07-12",
 "stage": "sense-split Stage A (V-A + V-B), LAUNCH-READY, NOT RUN",
 "judges": {
   "pA": {"id": "judge-pA-gpt56sol", "kind": "codex", "model": "gpt-5.6-sol",
           "note": "PRIMARY; npx-pinned codex CLI 0.144.1, reasoning low, read-only, server-side output schema (protocol carried from run-ontg2v2.py)"},
   "pB": {"id": "judge-pB-opus48", "kind": "claude", "model": "claude-opus-4-8",
           "note": "maintainer Haiku->Opus directive (issue #25); headless claude CLI, tools disabled, helper-key tolerance as in ontg2v2 --pb-model opus (ASM-1873/1874)"}
 },
 "rubric": "poc/ontology-import-g2-v2/prompt-template-v2.2.txt (v2.2 composite-hedge sentence-force rubric, byte-reused)",
 "channel_precondition": "adjudication section D pre-commitment: this pair judges V-A/V-B ONLY if the v2.2 pilot passes AC1>=0.65; else these same materials go to the two-human panel. This build spends nothing before that resolves.",
 "counts": {"va": len(va_rows), "vb": len(vb_rows), "cal_per_judge": CAL_PER_JUDGE},
 "seeds": seeds, "orders": orders,
 "cost_plan": plan,
 "input_pins": {rel: sha(os.path.join(REPO, rel)) for rel in INPUTS},
 "kernel_v1_gates_echo": manifest_kv1["gates"],
}
with open(os.path.join(MAT, "manifest.json"), "w") as f:
    f.write(json.dumps(manifest, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

print(json.dumps({"ok": True, "va": len(va_rows), "vb": len(vb_rows),
                  "expected_calls": calls, "expected_usd": plan["expected_usd_at_price_bound"],
                  "worst_case_usd_bound": plan["worst_case_usd_bound"]}))
