#!/usr/bin/env python3
"""
Generate the F1-K kernel-v1 PILOT explication batch (issue #33, §1.1 scholarly
explication gate + §1.2 WN-3.1 alignment gate). Benchmark-blind: reads only the
model-independent candidate pool (item counts), never model/gold outcomes.
$0 · no git · no registry · no freeze. colibri naming only.

Deterministic selection rule (frozen, recorded in pilot-review.md):
  P1  = candidate-pool.json rows with greedy_disjoint_m8==True AND
        header_cue_collision==False  (disjoint-eligible, header-clean; 2,397).
  R   = genus prefilter: gloss matches a frozen genus-differentia template set,
        which also fixes the kot-ast/1 frame family (agentive/act/state).
  Stratify by first-matching genus into AGENTIVE / ACT / STATE.
  Sort each stratum by WN-3.1 synset URN byte order (design §2.3 tiebreak 6).
  Round-robin [AGENTIVE, ACT, STATE], URN-smallest unused each cycle, to 15.

This file only *reproduces the selection* and writes provenance; the 15 glosses
and kot-ast/1 records are authored by hand below (PILOT_RECORDS).
"""
import json, hashlib, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
POOL = json.load(open(ROOT / "poc/scale/f1k-eligibility/candidate-pool.json"))
OUT_CONCEPTS = ROOT / "data/kernel-v1-pilot/concepts"

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ---- reproduce the deterministic selection -------------------------------
P1 = [x for x in POOL["candidates"]
      if x.get("greedy_disjoint_m8") and not x.get("header_cue_collision")]
STRATA = [
    ("AGENTIVE", [r"^someone who", r"^a person who", r"^a person that", r"^one who"]),
    ("ACT",      [r"^the act of", r"^an act of", r"^an event"]),
    ("STATE",    [r"^a state of", r"^the state of", r"^the quality of", r"^a feeling of"]),
]
def stratum(g):
    gl = g.lower().strip()
    for name, pats in STRATA:
        if any(re.match(p, gl) for p in pats):
            return name
    return None
buckets = {n: [] for n, _ in STRATA}
for x in P1:
    s = stratum(x["gloss"])
    if s:
        buckets[s].append(x)
for n in buckets:
    buckets[n].sort(key=lambda r: r["urn"])
order = ["AGENTIVE", "ACT", "STATE"]
idx = {n: 0 for n in order}
selected = []
while len(selected) < 15:
    for n in order:
        if idx[n] < len(buckets[n]):
            selected.append((n, buckets[n][idx[n]]))
            idx[n] += 1
            if len(selected) >= 15:
                break
POOL_BY_URN = {x["urn"]: x for _, x in selected}
SEL_URNS = [x["urn"] for _, x in selected]

# ---- AST builder helpers -------------------------------------------------
def sp(head=None, prime=None, kind_of=None, part_of=None, ref_of=None,
       det=None, quant=None, mods=None, bind=None, restrictedBy=None):
    o = {"kind": "sp"}
    if det: o["det"] = det
    if quant: o["quant"] = quant
    if mods: o["mods"] = mods
    if prime is not None:
        o["head"] = {"kind": "primeHead", "prime": prime}
    elif kind_of is not None:
        o["head"] = {"kind": "kindFrame", "of": kind_of}
    elif part_of is not None:
        o["head"] = {"kind": "partFrame", "of": part_of}
    elif ref_of is not None:
        o["head"] = {"kind": "refHead", "index": ref_of}
    else:
        o["head"] = head
    if bind is not None: o["bind"] = bind
    if restrictedBy is not None: o["restrictedBy"] = restrictedBy
    return o
def ref(i): return {"kind": "ref", "index": i}
def prime(p): return {"kind": "prime", "prime": p}
def concept(cid): return {"kind": "concept", "id": cid}
def mod(m, inten=None):
    o = {"mod": m}
    if inten: o["intensifier"] = inten
    return o
def kof(x): return x  # of-target passthrough (sp/ref/concept)
def pred(p, **roles): return {"type": "pred", "pred": p, "roles": roles}
def op(o, *args): return {"type": "op", "op": o, "args": list(args)}
def clause(c): return {"kind": "clause", "clause": c}
def quote(*cs): return {"kind": "quote", "clauses": list(cs)}
def temporal(o, anchor): return {"kind": "temporal", "op": o, "anchor": anchor}
NOW = prime("NOW")
def R(idx, kind): return {"index": idx, "refKind": kind}
def expl(frame, refs, clauses):
    return {"schema": "kot-ast/1", "frame": frame, "referents": refs, "clauses": clauses}

# convenience SP heads
def SOMETHING(**kw): return sp(prime="SOMETHING~THING", **kw)
def SOMEONE(**kw): return sp(prime="SOMEONE", **kw)
def PEOPLE(**kw): return sp(prime="PEOPLE", **kw)
def WHENTIME(**kw): return sp(prime="WHEN~TIME", **kw)

# ==========================================================================
#  THE 15 AUTHORED RECORDS
#  gloss   = scholarly K-carrier text (the d3 content)
#  mode    = reused-verbatim | light-edit | authored-fresh
#  bar     = self-assessment: 'meets' | 'borderline'  (+ reason)
#  ast_adq = kot-ast/1 semantic adequacy vs the gloss: 'faithful' | 'lossy'
# ==========================================================================
PILOT_RECORDS = {

"lover": dict(
  label="lover",
  gloss=("Someone who feels deep affection or romantic love toward another "
         "person, or who is the object of such love; especially a person with "
         "whom one shares an intimate romantic attachment."),
  mode="authored-fresh",
  bar=("meets", "clean genus-differentia; WN gloss was circular (lover/loves) "
       "and disjunctive, so authored fresh."),
  ast_adq=("lossy", "profile-1 renders affection + wishing the other well but "
           "cannot mark the romantic/sexual differentia; reads as a generalised "
           "well-wisher."),
  pattern="InstanceSchema; affection + benefactive want (cf. kernel-v0 friend)",
  explication=expl("InstanceSchema",
    [R(1,"SomeoneRef"), R(2,"SomeoneRef")],
    [ pred("THINK", experiencer=ref(1),
           topic=SOMEONE(det="OTHER~ELSE~ANOTHER", bind=2)),
      pred("FEEL", experiencer=ref(1), attribute=prime("GOOD")),
      pred("WANT", experiencer=ref(1),
           complement=clause(pred("FEEL", experiencer=ref(2),
                                   attribute=prime("GOOD")))),
    ]),
),

"peer": dict(
  label="peer (X is a peer of Y)",
  gloss=("A person who holds the same rank, standing, or status as another "
         "within a group, being neither above nor below them in position or "
         "authority."),
  mode="light-edit",
  bar=("meets", "WN core ('of equal standing with another in a group') is a "
       "clean genus-differentia; expanded from 11 words to meet the length "
       "convention and to make 'equal standing' explicit."),
  ast_adq=("lossy", "'equal standing' rendered spatially (neither above the "
           "other, both among the same people); social rank is not primitive."),
  pattern="RelationalSchema; ABOVE-negation pair for equal standing",
  explication=expl("RelationalSchema",
    [R(1,"SomeoneRef"), R(2,"SomeoneRef"), R(3,"SomeoneRef")],
    [ pred("BE-SOMEWHERE", undergoer=ref(1),
           locus=PEOPLE(quant="MUCH~MANY", bind=3)),
      pred("BE-SOMEWHERE", undergoer=ref(2), locus=ref(3)),
      op("NOT", pred("BE-SOMEWHERE", undergoer=ref(1), locus=ref(2),
                     manner=prime("ABOVE"))),
      op("NOT", pred("BE-SOMEWHERE", undergoer=ref(2), locus=ref(1),
                     manner=prime("ABOVE"))),
    ]),
),

"wrongdoer": dict(
  label="wrongdoer",
  gloss=("A person who does what moral standards or the law forbid; one who "
         "commits an offence, wrong, or misdeed against others or against "
         "established rules."),
  mode="light-edit",
  bar=("meets", "WN core ('transgresses moral or civil law') is clean and "
       "non-circular; expanded for length and to separate the two forbidding "
       "sources (morality / law)."),
  ast_adq=("faithful", "does many bad things that people do not want done — a "
           "sound NSM reading of transgression."),
  pattern="InstanceSchema; bad acts + collective DON'T-WANT (cf. thief)",
  explication=expl("InstanceSchema",
    [R(1,"SomeoneRef"), R(2,"SomethingRef")],
    [ pred("DO", agent=ref(1),
           undergoer=SOMETHING(quant="MUCH~MANY", mods=[mod("BAD")], bind=2)),
      pred("DON'T-WANT", experiencer=PEOPLE(quant="MUCH~MANY"),
           complement=clause(pred("DO", agent=ref(1), undergoer=ref(2)))),
    ]),
),

"artists-model": dict(
  label="artist's model",
  gloss=("A person who poses, keeping still in a chosen attitude, so that a "
         "painter or sculptor can observe them and make a picture or figure of "
         "them."),
  mode="light-edit",
  bar=("meets", "WN core ('poses for a painter or sculptor') is clean; expanded "
       "to state the defining condition (holding still to be depicted)."),
  ast_adq=("lossy", "'painter/sculptor/picture' collapse to 'another makes "
           "something like this someone'; the art differentia is not primitive."),
  pattern="InstanceSchema; hold-still + perception-licensed depiction",
  explication=expl("InstanceSchema",
    [R(1,"SomeoneRef"), R(2,"SomeoneRef"), R(3,"SomethingRef")],
    [ op("NOT", pred("MOVE", undergoer=ref(1),
                     duration=prime("FOR-SOME-TIME"))),
      pred("SEE", experiencer=SOMEONE(det="OTHER~ELSE~ANOTHER", bind=2),
           stimulus=ref(1)),
      op("BECAUSE",
         pred("SEE", experiencer=ref(2), stimulus=ref(1)),
         pred("DO", agent=ref(2), undergoer=SOMETHING(bind=3))),
      op("LIKE", ref(3), ref(1)),
    ]),
),

"bill-poster": dict(
  label="bill poster",
  gloss=("Someone whose work is to fix printed notices, posters, or placards "
         "onto walls, boards, and other public surfaces, so that many people "
         "will see them."),
  mode="light-edit",
  bar=("borderline", "clean WN gloss, but the AST cannot carry 'printed "
       "notices / words', so the reviewer must judge the prose alone; a "
       "reviewer expecting AST-prose parity may fail it."),
  ast_adq=("lossy", "'bills with words on walls' reduce to 'puts many things "
           "onto big things where people can see them'."),
  pattern="InstanceSchema; place-artefacts-for-public-view",
  explication=expl("InstanceSchema",
    [R(1,"SomeoneRef"), R(2,"SomethingRef"), R(3,"SomethingRef")],
    [ pred("DO", agent=ref(1),
           undergoer=SOMETHING(quant="MUCH~MANY", bind=2)),
      pred("BE-SOMEWHERE", undergoer=ref(2),
           locus=SOMETHING(mods=[mod("BIG")], bind=3),
           manner=prime("ABOVE")),
      op("CAN", pred("SEE", experiencer=PEOPLE(quant="MUCH~MANY"),
                     stimulus=ref(2))),
    ]),
),

"appearance": dict(
  label="appearance",
  gloss=("The event of someone or something coming to be seen, especially by "
         "coming before other people in a public place; a becoming-present to "
         "view."),
  mode="authored-fresh",
  bar=("meets", "WN gloss ('the act of appearing in public view') is circular; "
       "authored fresh around the seeable-before/after core."),
  ast_adq=("faithful", "before the time none could see it, after it they can — "
           "a clean rendering of coming into view."),
  pattern="InstanceSchema; SEE polarity across a time boundary",
  explication=expl("InstanceSchema",
    [R(1,"SomethingRef"), R(2,"SomethingRef"), R(3,"TimeRef")],
    [ pred("HAPPEN", undergoer=ref(1),
           time=WHENTIME(det="SOME", bind=3)),
      op("BEFORE", ref(3),
         op("NOT", op("CAN", pred("SEE",
              experiencer=PEOPLE(quant="MUCH~MANY"),
              stimulus=SOMETHING(bind=2))))),
      op("AFTER", ref(3),
         op("CAN", pred("SEE", experiencer=PEOPLE(quant="MUCH~MANY"),
                        stimulus=ref(2)))),
    ]),
),

"apparition": dict(
  label="apparition",
  gloss=("An occasion on which something comes suddenly into view when no one "
         "expected to see it, so that those present are taken by surprise; a "
         "sudden, unlooked-for becoming-visible."),
  mode="authored-fresh",
  bar=("borderline", "genuinely distinct from 'appearance' only by the "
       "sudden/unexpected differentia; deliberately near-synonymous to probe "
       "whether the reviewer discriminates the two senses."),
  ast_adq=("lossy", "'surprise' rendered as 'people did not know they would see "
           "it'; suddenness rendered as MOMENT duration."),
  pattern="InstanceSchema; appearance + MOMENT + prior not-knowing",
  explication=expl("InstanceSchema",
    [R(1,"SomethingRef"), R(2,"SomethingRef"), R(3,"TimeRef")],
    [ pred("HAPPEN", undergoer=ref(1),
           time=WHENTIME(det="SOME", bind=3), duration=prime("MOMENT")),
      op("AFTER", ref(3),
         op("CAN", pred("SEE", experiencer=PEOPLE(quant="MUCH~MANY"),
                        stimulus=SOMETHING(bind=2)))),
      op("BEFORE", ref(3),
         op("NOT", pred("KNOW", experiencer=PEOPLE(quant="MUCH~MANY"),
              complement=clause(pred("SEE",
                  experiencer=PEOPLE(quant="MUCH~MANY"), stimulus=ref(2)))))),
    ]),
),

"exit": dict(
  label="exit",
  gloss=("The act of going out of a place; a movement by which someone or "
         "something passes from inside an enclosure or space to a position "
         "outside it."),
  mode="light-edit",
  bar=("meets", "WN gloss ('the act of going out') is non-circular but too "
       "terse; expanded to state the inside-to-outside movement."),
  ast_adq=("faithful", "inside before, moves, not inside after — an exact NSM "
           "reading of going out."),
  pattern="InstanceSchema; INSIDE polarity across a MOVE",
  explication=expl("InstanceSchema",
    [R(1,"SomethingRef"), R(2,"SomethingRef"), R(3,"TimeRef")],
    [ pred("BE-SOMEWHERE", undergoer=ref(1),
           locus=SOMETHING(bind=2), manner=prime("INSIDE")),
      pred("MOVE", undergoer=ref(1), time=WHENTIME(det="SOME", bind=3)),
      op("AFTER", ref(3),
         op("NOT", pred("BE-SOMEWHERE", undergoer=ref(1), locus=ref(2),
                        manner=prime("INSIDE")))),
    ]),
),

"ransom": dict(
  label="ransom",
  gloss=("The act of securing the release of a captive by paying the price "
         "demanded for it; also the sum so paid, or the freeing thereby "
         "obtained."),
  mode="authored-fresh",
  bar=("borderline", "the WN synset gloss ('the act of freeing from captivity "
       "or punishment') OMITS the defining payment; authoring it in restores "
       "the true intension but arguably narrows the synset — an alignment "
       "call the human reviewer must make."),
  ast_adq=("lossy", "'pays the price' reduces to 'does something with a good "
           "thing'; captivity reduces to a captor's DON'T-WANT-to-go."),
  pattern="InstanceSchema; payment-conditioned release",
  explication=expl("InstanceSchema",
    [R(1,"SomeoneRef"), R(2,"SomeoneRef"), R(3,"SomethingRef"),
     R(4,"SomeoneRef")],
    [ pred("DON'T-WANT", experiencer=SOMEONE(bind=4),
           complement=clause(pred("MOVE", undergoer=ref(1)))),
      op("BECAUSE",
         pred("DO", agent=SOMEONE(det="OTHER~ELSE~ANOTHER", bind=2),
              undergoer=SOMETHING(mods=[mod("GOOD")], bind=3)),
         op("CAN", pred("MOVE", undergoer=ref(1)))),
    ]),
),

"throw": dict(
  label="throw",
  gloss=("The act of sending something through the air by a rapid movement of "
         "the arm and hand, releasing it so that it travels away from the "
         "thrower."),
  mode="light-edit",
  bar=("meets", "WN parenthetical ('propelling something with a rapid movement "
       "of the arm and wrist') is the real definition; led with it and dropped "
       "the circular 'the act of throwing'."),
  ast_adq=("faithful", "acts on a thing with a body-part so that it moves far — "
           "a good primitive reading of propelling."),
  pattern="InstanceSchema; body-part instrument + resulting far-motion",
  explication=expl("InstanceSchema",
    [R(1,"SomeoneRef"), R(2,"SomethingRef")],
    [ pred("DO", agent=ref(1), undergoer=SOMETHING(bind=2),
           instrument=sp(part_of=sp(prime="BODY"))),
      op("BECAUSE",
         pred("DO", agent=ref(1), undergoer=ref(2)),
         pred("MOVE", undergoer=ref(2), manner=prime("FAR"))),
      pred("BE-SOMEWHERE", undergoer=ref(2), locus=ref(1),
           manner=prime("FAR")),
    ]),
),

"cheerfulness": dict(
  label="cheerfulness",
  gloss=("A disposition marked by good spirits and evident gladness, such that "
         "one readily feels contentment and lifts the mood of those nearby."),
  mode="authored-fresh",
  bar=("meets", "WN gloss ('being cheerful and dispelling gloom') is circular; "
       "authored fresh around felt-gladness that spreads to others."),
  ast_adq=("faithful", "feels good, and others near feel good — captures both "
           "the felt cheer and the gloom-dispelling clause."),
  pattern="WhenTrue; felt gladness + spread to others",
  explication=expl("WhenTrue",
    [R(1,"SomeoneRef"), R(2,"SomeoneRef")],
    [ pred("FEEL", experiencer=ref(1), attribute=prime("GOOD")),
      op("WHEN",
         pred("BE-SOMEWHERE", undergoer=PEOPLE(quant="MUCH~MANY", bind=2),
              locus=ref(1)),
         pred("FEEL", experiencer=ref(2), attribute=prime("GOOD"))),
    ]),
),

"changelessness": dict(
  label="changelessness",
  gloss=("The quality of remaining the same through time, such that a thing "
         "stays as it is and does not come to be other than it was."),
  mode="authored-fresh",
  bar=("borderline", "WN gloss ('being unchangeable') is circular; authored "
       "fresh, but 'change' is not among the primes, so both prose and AST lean "
       "on the SAME/OTHER contrast — the reviewer should check that this is "
       "faithful, not merely available."),
  ast_adq=("lossy", "'does not change' rendered as 'for a long time is the same "
           "kind of thing; is not another kind of thing'."),
  pattern="WhenTrue; THE-SAME / OTHER contrast over A-LONG-TIME",
  explication=expl("WhenTrue",
    [R(1,"SomethingRef")],
    [ pred("BE-SPEC", undergoer=ref(1),
           attribute=sp(det="THE-SAME", kind_of=SOMETHING()),
           duration=prime("A-LONG-TIME")),
      op("NOT", pred("BE-SPEC", undergoer=ref(1),
           attribute=sp(det="OTHER~ELSE~ANOTHER", kind_of=SOMETHING()))),
    ]),
),

"fidelity": dict(
  label="fidelity",
  gloss=("Steadfast faithfulness in keeping one's promises and obligations to "
         "another, so that one continues to act as one has undertaken and does "
         "not betray the trust placed in one."),
  mode="authored-fresh",
  bar=("meets", "WN gloss ('being faithful') is circular and one word of "
       "content; authored fresh around keeping-one's-word plus not-betraying."),
  ast_adq=("faithful", "says to another about a thing, does that thing, and "
           "does not want the other to feel bad — a sound reading of keeping "
           "faith."),
  pattern="WhenTrue; undertaking + follow-through + non-betrayal",
  explication=expl("WhenTrue",
    [R(1,"SomeoneRef"), R(2,"SomeoneRef"), R(3,"SomethingRef")],
    [ pred("SAY", agent=ref(1),
           addressee=SOMEONE(det="OTHER~ELSE~ANOTHER", bind=2),
           topic=SOMETHING(bind=3)),
      pred("DO", agent=ref(1), undergoer=ref(3)),
      pred("DON'T-WANT", experiencer=ref(1),
           complement=clause(pred("FEEL", experiencer=ref(2),
                                   attribute=prime("BAD")))),
    ]),
),

"continuousness": dict(
  label="continuousness",
  gloss=("The quality of a thing that goes on without break or pause, "
         "continuing as one unbroken whole through time rather than stopping "
         "and starting."),
  mode="authored-fresh",
  bar=("meets", "WN gloss ('something that continues without end or "
       "interruption') is circular; authored fresh around unbroken persistence."),
  ast_adq=("faithful", "happens for a long time; there is no later time at "
           "which it does not happen — a clean reading of unbroken continuity."),
  pattern="WhenTrue; long duration + no interrupting after-gap",
  explication=expl("WhenTrue",
    [R(1,"SomethingRef"), R(2,"TimeRef")],
    [ pred("HAPPEN", undergoer=ref(1), duration=prime("A-LONG-TIME")),
      op("NOT",
         op("AFTER", WHENTIME(det="SOME", bind=2),
            op("NOT", pred("HAPPEN", undergoer=ref(1))))),
    ]),
),

"wealth": dict(
  label="wealth (profuse abundance)",
  gloss=("A great abundance of some valued thing, such that there is far more "
         "of it present than is usual or than could be needed."),
  mode="authored-fresh",
  bar=("borderline", "this is the ABUNDANCE sense of the eligible synset "
       "(n-05123428), NOT the riches/money sense a reviewer may expect; the "
       "gloss must make the sense unmistakable or the WN alignment check will "
       "read as the wrong sense."),
  ast_adq=("faithful", "there are very many good things of the kind; there are "
           "not few — an adequate reading of 'profuse abundance'."),
  pattern="InstanceSchema; MUCH-MANY of a good kind + not-few",
  explication=expl("InstanceSchema",
    [R(1,"SomethingRef")],
    [ pred("THERE-IS", undergoer=sp(quant="MUCH~MANY", mods=[mod("GOOD")],
                                    kind_of=ref(1))),
      op("NOT", pred("THERE-IS",
           undergoer=sp(quant="LITTLE~FEW", kind_of=ref(1)))),
    ]),
),
}

# ---- slug -> selected synset (deterministic order) -----------------------
SLUG_ORDER = ["lover","appearance","cheerfulness","peer","apparition",
              "changelessness","wrongdoer","exit","fidelity","artists-model",
              "ransom","continuousness","bill-poster","throw","wealth"]
# map each slug to its selected pool row by lemma match on the selection
LEMMA_OF = {
  "lover":"lover","appearance":"appearance","cheerfulness":"cheerfulness",
  "peer":"peer","apparition":"apparition","changelessness":"changelessness",
  "wrongdoer":"wrongdoer","exit":"exit","fidelity":"fidelity",
  "artists-model":"artist's model","ransom":"ransom",
  "continuousness":"continuousness","bill-poster":"bill poster",
  "throw":"throw","wealth":"wealth",
}
# resolve the exact selected URN per slug from the selection list
SEL_BY_LEMMA = {}
for _n, x in selected:
    SEL_BY_LEMMA[x["lemmas"][0]] = x

assert set(PILOT_RECORDS) == set(SLUG_ORDER), "slug mismatch"

rows_meta = []
for slug in SLUG_ORDER:
    rec = PILOT_RECORDS[slug]
    poolrow = SEL_BY_LEMMA[LEMMA_OF[slug]]
    wn_urn = poolrow["urn"]
    wn_gloss = poolrow["gloss"]
    gloss = rec["gloss"]
    doc = {
        "id": f"urn:kernel-v1-pilot:{slug}",
        "label": rec["label"],
        "status": "pilot",
        "pattern": rec["pattern"],
        "gloss": gloss,
        "notes": f"AST adequacy: {rec['ast_adq'][0]} — {rec['ast_adq'][1]}",
        "references": [],
        "explication": rec["explication"],
        "provenance": {
            "wn31_synset": wn_urn.replace("urn:lexical-wn31:", "urn:lexical-wn31:"),
            "wn31_pos": poolrow["pos"],
            "wn31_lemmas": poolrow["lemmas"],
            "definition_mode": rec["mode"],
            "source": "WordNet-3.1 synset gloss (candidate-pool.json, benchmark-blind item screen)",
            "source_gloss": wn_gloss,
            "source_gloss_sha256": sha256(wn_gloss),
            "gloss_sha256": sha256(gloss),
            "m_test_screen": poolrow["m_total"],
            "bar_self_assessment": rec["bar"][0],
            "bar_note": rec["bar"][1],
            "benchmark_blind": True,
        },
    }
    (OUT_CONCEPTS / f"{slug}.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    rows_meta.append({
        "slug": slug, "label": rec["label"], "wn31_synset": wn_urn,
        "pos": poolrow["pos"], "mode": rec["mode"], "bar": rec["bar"][0],
        "bar_note": rec["bar"][1], "ast_adq": rec["ast_adq"][0],
        "gloss": gloss, "wn_gloss": wn_gloss, "m_test_screen": poolrow["m_total"],
        "gloss_sha256": sha256(gloss), "source_gloss_sha256": sha256(wn_gloss),
    })

# stratum labels for the write-up
STRAT_OF = {x["urn"]: n for n, x in selected}
json.dump({
    "built": "designer-31 F1-K kernel-v1 PILOT explication batch ($0, benchmark-blind)",
    "issue": "#33",
    "selection_rule": ("P1(disjoint_m8 & header-clean) -> genus prefilter R -> "
                       "stratify AGENTIVE/ACT/STATE -> URN byte order -> "
                       "round-robin to 15"),
    "selected_urns": SEL_URNS,
    "strata": {n: [x["urn"] for m, x in selected if m == n] for n in order},
    "records": rows_meta,
}, open(ROOT / "poc/scale/f1k-explication/pilot-manifest.json", "w"),
    indent=2, ensure_ascii=False)

print("wrote", len(SLUG_ORDER), "records to", OUT_CONCEPTS)
print("selection (round-robin AGENTIVE/ACT/STATE, URN order):")
for n, x in selected:
    print(f"  {n:8s} {x['lemmas'][0]:16s} {x['urn']}")
