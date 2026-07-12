#!/usr/bin/env python3
"""build-softtype.py -- deterministic ONT-TYPE-G2/1 soft-typing build.

Implements docs/next/design/ontology-import-plan.md sections 2-6 for the
issue-#20 go/no-go experiment (registry/experiments/g2-import.json):
maps the 84 frozen g2 item slots (poc/g2/materials/items.jsonl) to
BFO-anchored SOFT type expectations refined by SUMO selectional evidence
and FrameNet valency evidence, and renders the A1/A2/A3 experiment arms
plus per-arm deranged-sort probes.

DESIGN AUTHORITY: the per-slot bridge table below is AUTHORED,
EXPERIMENT-ONLY content (plan Phase 3, "experiment-only bridge
candidates ... using the five pattern families"). Every entry is a
kot-ont-bridge/1 CANDIDATE: authority=candidate, identity_bearing=false,
never endorsed by this script. Soft-type records carry binding:false and
effect:rank-only (plan section 3.3, load-bearing); a validator here
fails closed if any record omits them or if any hard operational law
(rdfs:domain / rdfs:range / owl:disjointWith / existential-generating
rule over kernel or world entities) would be emitted.

Deterministic: no RNG, no network, no timestamps beyond the fixed
BUILD_DATE constant; output bytes are a pure function of the pinned
inputs and this file. Fail-closed: any missing source URN, pin
mismatch, or slot-count drift aborts (ERR_ONT_*).

Outputs (task-directed path data/onto-softtype/ carrying the plan
section-6 content list; the plan's provisional name for the same
artifact set was data/ontology-import-v0/):
  data/onto-softtype/manifest.json
  data/onto-softtype/bfo-anchor.jsonl
  data/onto-softtype/bridge-candidates.jsonl
  data/onto-softtype/soft-type-candidates.jsonl
  data/onto-softtype/conflicts.jsonl
  data/onto-softtype/source-attribution.json
  data/onto-softtype/MAPPING.md
  poc/ontology-import-g2/materials/arm-a0-baseline.jsonl
  poc/ontology-import-g2/materials/arm-a1-bfo.jsonl
  poc/ontology-import-g2/materials/arm-a2-bfo-sumo.jsonl
  poc/ontology-import-g2/materials/arm-a3-bfo-sumo-framenet.jsonl
  poc/ontology-import-g2/materials/probes-a1.jsonl / -a2 / -a3
  poc/ontology-import-g2/materials/manifest.json   (order seeds)
  poc/ontology-import-g2/materials/render-manifest.json
  poc/ontology-import-g2/materials/generation-report.json
"""
import hashlib
import json
import os
import sys

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
OUT_DATA = os.path.join(REPO, "data/onto-softtype")
OUT_POC = os.path.join(REPO, "poc/ontology-import-g2/materials")
BUILD_DATE = "2026-07-12"          # fixed constant, not a clock read
SCHEMA_BRIDGE = "kot-ont-bridge/1"
SCHEMA_SOFT = "kot-soft-type/1"

# ---- pinned inputs (plan section 2 source freeze; ERR_ONT_PIN) ----
PINS = {
    "data/onto-obo/bfo.jsonl":
        "c845126441764932fe7de16fd3031aeaf4c9c19875f26165b3452dff7396e42a",
    "data/onto-sumo/terms.jsonl":
        "47d4d8be71a3837372bdcf343d4684065ff62adaa76f03b0faac059013be20e9",
    "data/onto-sumo/axioms.jsonl":
        "d5ee964faa5585c37899de3bf301fea49c7de6cf055e100f90b503bcc498ce37",
    "data/onto-framenet/frames.jsonl":
        "08f4387fdc91f6804b6604e20ad98494eac351b49e973265f3565e8de8c88f58",
    "data/onto-framenet/frame-relations.jsonl":
        "af881b7544a4829554ab42f8dc98b18b7880106928e923accf4afebd36d92b4d",
    "poc/g2/materials/items.jsonl":
        "7a4728840550227703338880a79f61491a3c93e5022f07215631f6caa7077008",
    "poc/g2/materials/prompt-template.txt":
        "d8724154a740e8c0e7174f9a083f6a8411dfb5fda17c87d6d52acfb4da31dcac",
    "poc/g2/labels-proxy.jsonl":
        "93a124478b8dba411bfd1a9fd07cbc96e874def8e6ac819202c54c1b121754b3",
}
ALIGN_FILES = {         # consulted, cited where present (hash recorded)
    "sumo": "data/onto-sumo/alignment-kernel-v0.json",
    "framenet": "data/onto-framenet/alignment-kernel-v0.json",
    "obo": "data/onto-obo/alignment-kernel-v0.json",
}


def die(msg):
    sys.stderr.write("ERR_ONT: %s\n" % msg)
    sys.exit(2)


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def sha_str(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def jload(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def jdump_line(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False) + "\n"


# ============================================================
# AUTHORED BRIDGE TABLE (experiment-only candidates; plan Phase 3)
# ------------------------------------------------------------
# Per g2 slot id:
#   fam : pattern family (plan section 5; one of the five reviewed
#         families -- event-action | agent-intention-goal |
#         generic-type-vs-kind | role-vs-phase | quality-vs-disposition)
#   bfo : BFO class label anchoring the tested position, or None
#         (None / "entity" => vacuous at A1 by the plan's vacuity rule)
#   sumo: list of SUMO term names cited as selectional-preference
#         evidence (A2+), [] if none
#   fn  : FrameNet frame name cited as valency evidence (A3), or None
#   rank: strong | moderate | weak | underdetermined (plan section 4.4)
#   a1  : the A1 statement (BFO-anchored; universal part only)
#   a2  : clause appended at A2 (SUMO-backed preference; "Normally...")
#   a3  : clause appended at A3 (FrameNet-backed valency; "Typically...")
# Statements keep the tested argument/relationship explicit (a
# statement that omits it scores 0 by the frozen slot-scoring rule)
# and make all soft modality explicit (plan section 7.2).
# ============================================================

def _t(noun_phrase, subject_clause):
    """Template for the ten R4 time-existential slots."""
    return (
        "In every case of %s as described above, %s happens at some time "
        "— there is a time at which it takes place." % (noun_phrase, subject_clause),
        "Normally one can say when it happened, at least roughly.",
        None,
    )


BRIDGE = {
 # -- archived --------------------------------------------------------
 "g2:pi:000": dict(fam="agent-intention-goal", bfo="process",
  sumo=["Keeping", "Putting"], fn="Storing", rank="moderate",
  a1="Whenever someone or something is archived, an archiving happened "
     "— something took place in time by which it was put away for keeping.",
  a2="Normally this putting-away is done on purpose, so that the thing is "
     "kept but out of the way.",
  a3="Typically there is someone — or a tool or system acting for someone "
     "— that does the archiving, the thing archived, and a place or "
     "collection where it is kept."),
 # -- begin -----------------------------------------------------------
 "g2:pi:001": dict(fam="event-action", bfo="occurrent",
  sumo=["BeginFn", "Process"], fn=None, rank="strong",
  a1="In every case of “begin (happening X begins at time T)” as "
     "described above, X is something that happens or goes on in time (a "
     "happening or process) — not a person, a place, or a time.",
  a2="Normally X is the kind of happening that lasts for some time once it "
     "has begun.",
  a3=None),
 "g2:pi:002": dict(fam="event-action", bfo="temporal region",
  sumo=["TimePosition", "BeginFn"], fn=None, rank="strong",
  a1="In every case of “begin (happening X begins at time T)” as "
     "described above, T is a time — a moment or stretch of time.",
  a2="Normally T is thought of as the moment the happening starts.",
  a3=None),
 # -- believe ---------------------------------------------------------
 "g2:pi:003": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["believes", "CognitiveAgent"], fn="Becoming_aware", rank="strong",
  a1="In every case of “believe (X believes Y)” as described above, "
     "X is someone or something that exists on its own and lasts through "
     "time — not a time, a place, or a mere happening.",
  a2="Normally X is someone who can think — a person, or a being or "
     "group with a mind.",
  a3="Typically X is the one in whose mind the believing happens (the "
     "believer)."),
 "g2:pi:004": dict(fam="agent-intention-goal",
  bfo="generically dependent continuant",
  sumo=["believes", "Formula"], fn="Becoming_aware", rank="strong",
  a1="In every case of “believe (X believes Y)” as described above, "
     "Y is something that can be thought — a content, the kind of thing "
     "that could also be put into words.",
  a2="Normally Y is something that can be so or not so — the kind of "
     "content that can be true or false.",
  a3="Typically Y, the content believed, can be about anything — a "
     "person, a place, a thing, or another happening."),
 # -- birth -----------------------------------------------------------
 "g2:pi:005": dict(fam="event-action", bfo="process",
  sumo=["Birth", "Process"], fn="Being_born", rank="strong",
  a1="Every birth is a happening — something that takes place in time "
     "(an event), not a lasting object.",
  a2="Normally a birth is a bodily happening in the life of a living thing.",
  a3="Typically a birth involves the one who is born (a child or young), "
     "and it happens at some time and place."),
 "g2:pi:006": dict(fam="event-action", bfo="temporal region",
  sumo=["Birth", "TimePoint"], fn="Event", rank="strong",
  a1=_t("a birth", "the birth")[0], a2=_t("", "")[1], a3=None),
 # -- bookmark --------------------------------------------------------
 "g2:pi:007": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["ContentBearingObject", "Icon"], fn="Records", rank="moderate",
  a1="Every bookmark is a kept mark or record — something that stands "
     "for something else so that someone can come back to it; it is not "
     "itself a happening or a time.",
  a2="Normally a bookmark is a small piece of stored information — a "
     "mark, a note, or an entry that carries what it says in signs or words.",
  a3="Typically a bookmark is a record kept about something — the page "
     "or place it points back to."),
 "g2:pi:008": dict(fam="agent-intention-goal", bfo="process",
  sumo=["IntentionalProcess"], fn="Recording", rank="moderate",
  a1="In every case of a bookmark, it was made — a making or saving of "
     "it happened at some time.",
  a2="Normally it is made on purpose, so that something can be found again.",
  a3="Typically there is someone — or a tool or program acting for "
     "someone — that makes or keeps the bookmark."),
 "g2:pi:009": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["ContentBearingObject"], fn="Records", rank="moderate",
  a1="In every case of a bookmark, there is something the bookmark marks "
     "or points to — something other than the bookmark itself.",
  a2="Normally what it points to is a place in something made of words or "
     "signs — a page, a spot, an address.",
  a3="Typically the marked thing exists separately and can be gone back "
     "to again and again."),
 # -- break -----------------------------------------------------------
 "g2:pi:010": dict(fam="event-action", bfo="entity",
  sumo=["Damaging", "AutonomousAgent"], fn="Cause_to_fragment", rank="strong",
  a1="In every case of “break (X breaks Y)” as described above, X "
     "is what makes the breaking happen — someone or something.",
  a2="Normally X is someone — a person or other living being — "
     "acting on the thing.",
  a3="But X can also be a thing or a happening that causes the breaking "
     "— a storm, a fall, a blow."),
 "g2:pi:011": dict(fam="event-action", bfo="material entity",
  sumo=["Damaging", "Object"], fn="Cause_to_fragment", rank="strong",
  a1="In every case of “break (X breaks Y)” as described above, Y "
     "is a thing that can be in one piece and then not — something with "
     "a body or material to it, not a time and not a bare idea.",
  a2="Normally Y is a whole object — one thing that comes apart or "
     "stops holding together.",
  a3="Typically the breaking leaves pieces, or leaves Y no longer working "
     "as it should."),
 "g2:pi:012": dict(fam="event-action", bfo="temporal region",
  sumo=["Damaging", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of “break (X breaks Y)” as described above, "
     "the breaking happens at some time — there is a time at which it "
     "takes place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- broken ----------------------------------------------------------
 "g2:pi:014": dict(fam="quality-vs-disposition", bfo="quality",
  sumo=["Damaging", "Attribute"], fn="Render_nonfunctional", rank="moderate",
  a1="Whenever someone or something is broken, being broken is a way that "
     "thing now is — a condition of it, not something separate from it.",
  a2="Normally it is broken because at some earlier time a breaking "
     "happened to it.",
  a3="Typically a broken thing no longer holds together or no longer works "
     "as it should."),
 # -- cause -----------------------------------------------------------
 "g2:pi:015": dict(fam="event-action", bfo="occurrent",
  sumo=["causes", "Process"], fn="Causation", rank="strong",
  a1="In every case of “cause (happening X causes happening Y)” as "
     "described above, X is something that happens or is the case — a "
     "happening or situation, not a lasting object, a place, or a time.",
  a2="Normally X is itself a happening — something going on that makes "
     "the other happening come about.",
  a3="Typically one can point to X as the answer to why Y happened."),
 "g2:pi:016": dict(fam="event-action", bfo="occurrent",
  sumo=["causes", "Process"], fn="Causation", rank="strong",
  a1="In every case of “cause (happening X causes happening Y)” as "
     "described above, Y is something that happens or comes about — a "
     "happening or outcome, not a lasting object, a place, or a time.",
  a2="Normally Y is a happening that would not have come about, or not in "
     "that way, without X.",
  a3="Typically Y comes after X, or while X is going on — not before."),
 "g2:pi:017": dict(fam="event-action", bfo="temporal region",
  sumo=["causes", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of “cause (happening X causes happening Y)” as "
     "described above, the causing happens at some time — there is a "
     "time at which it takes place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- celebration -----------------------------------------------------
 "g2:pi:018": dict(fam="event-action", bfo="process",
  sumo=["SocialInteraction", "Ceremony"], fn="Social_event", rank="strong",
  a1="Every celebration is a happening — something people do that "
     "takes place in time (an event).",
  a2="Normally it is a social happening: people together doing something "
     "because something good happened or matters to them.",
  a3="Typically there are people taking part — those attending or "
     "celebrating."),
 "g2:pi:020": dict(fam="event-action", bfo="process",
  sumo=["IntentionalProcess", "SocialInteraction"], fn="Social_event",
  rank="strong",
  a1="In every case of a celebration, something happens — there are "
     "things done as part of it.",
  a2="Normally these are things people do on purpose — the celebrating "
     "itself.",
  a3="Typically this includes doings shared by those taking part."),
 # -- change ----------------------------------------------------------
 "g2:pi:021": dict(fam="event-action", bfo="continuant",
  sumo=["InternalChange", "Object"], fn="Undergo_change", rank="moderate",
  a1="In every case of a change, there is something that changes — "
     "something that was one way before, and another way after.",
  a2="Normally that something is there both before and after — it "
     "lasts through the change.",
  a3="Typically one can say what it was like at first and what it became."),
 "g2:pi:022": dict(fam="event-action", bfo="temporal region",
  sumo=["InternalChange", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of a change, it happens at some time — there is a "
     "time at which the change takes place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- condolence ------------------------------------------------------
 "g2:pi:023": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["LinguisticCommunication"], fn="Communication", rank="moderate",
  a1="Every condolence is something said — words, spoken or written, "
     "offered to someone.",
  a2="Normally the words say that the one offering them feels for someone "
     "over something bad — most often a death or a loss.",
  a3="Typically there is a message with a content, and a way it is given "
     "— said, written, or sent."),
 "g2:pi:025": dict(fam="role-vs-phase", bfo="role",
  sumo=["LinguisticCommunication", "Human"], fn="Contacting", rank="moderate",
  a1="In every case of a condolence, the words are offered to someone "
     "— there is one the condolence is for.",
  a2="Normally that one is a person other than the one speaking — the "
     "bereaved or the one suffering the loss.",
  a3="Typically the words are addressed to that person directly."),
 "g2:pi:026": dict(fam="role-vs-phase", bfo="role",
  sumo=["LinguisticCommunication", "Human"], fn="Communication",
  rank="moderate",
  a1="In every case of a condolence, someone offers the words — there "
     "is a speaker or writer of them.",
  a2="Normally a person, or people, expressing their sympathy.",
  a3="Typically the one offering it feels, or at least expresses, sorrow "
     "for the other."),
 # -- conversation ----------------------------------------------------
 "g2:pi:027": dict(fam="event-action", bfo="process",
  sumo=["Speaking", "SocialInteraction"], fn="Discussion", rank="strong",
  a1="Every conversation is a happening — an exchange that takes place "
     "in time (an event).",
  a2="Normally it is a social happening: people speaking with one another.",
  a3="Typically there are two or more people taking turns saying things to "
     "each other."),
 "g2:pi:028": dict(fam="role-vs-phase", bfo="role",
  sumo=["SocialInteraction", "Human"], fn="Discussion", rank="strong",
  a1="In every case of a conversation, words are said to someone — "
     "those speaking are speaking to someone.",
  a2="Normally to someone else: a conversation has more than one person "
     "in it.",
  a3="Typically each person in it is in turn a speaker and a listener."),
 "g2:pi:029": dict(fam="role-vs-phase", bfo="role",
  sumo=["Speaking", "Human"], fn="Discussion", rank="strong",
  a1="In every case of a conversation, someone says things — there is "
     "at least one person speaking.",
  a2="Normally the ones in it are persons speaking with words.",
  a3="Typically more than one of them speaks over its course."),
 # -- death -----------------------------------------------------------
 "g2:pi:030": dict(fam="event-action", bfo="process",
  sumo=["Death", "Process"], fn="Death", rank="strong",
  a1="Every death is a happening — something that takes place in time "
     "(an event).",
  a2="Normally it is the ending of a life — a bodily happening in a "
     "living thing.",
  a3="Typically there is the one who dies, and a time at which it happens."),
 "g2:pi:031": dict(fam="event-action", bfo="material entity",
  sumo=["Death", "Organism"], fn="Death", rank="strong",
  a1="In every case of a death, something living dies — there is one "
     "whose death it is.",
  a2="Normally a living thing — a person, an animal, a plant.",
  a3="Typically we speak of the death of someone, or of some living thing, "
     "in particular."),
 "g2:pi:032": dict(fam="event-action", bfo="temporal region",
  sumo=["Death", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of a death, it happens at some time — there is a "
     "time at which the death takes place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- end -------------------------------------------------------------
 "g2:pi:033": dict(fam="event-action", bfo="occurrent",
  sumo=["EndFn", "Process"], fn="Process_end", rank="strong",
  a1="In every case of “end (happening X ends at time T)” as "
     "described above, X is something that happens or goes on in time (a "
     "happening or process) — not a person, a place, or a time.",
  a2="Normally X is the kind of happening that was going on for some time "
     "before it ended.",
  a3="Typically after T, the happening X is no longer going on."),
 "g2:pi:034": dict(fam="event-action", bfo="temporal region",
  sumo=["TimePosition", "EndFn"], fn="Process_end", rank="strong",
  a1="In every case of “end (happening X ends at time T)” as "
     "described above, T is a time — a moment or stretch of time.",
  a2="Normally T is thought of as the moment the happening stops.",
  a3="Typically nothing of X goes on after T."),
 # -- event -----------------------------------------------------------
 "g2:pi:035": dict(fam="event-action", bfo="temporal region",
  sumo=["Process", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of a event, it happens at some time — there is a "
     "time at which the event takes place.",
  a2="Normally one can say when it happened, at least roughly.",
  a3="Typically it also happens somewhere — there is a place to it as "
     "well as a time."),
 # -- find ------------------------------------------------------------
 "g2:pi:036": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["Discovering", "CognitiveAgent"], fn="Locating", rank="strong",
  a1="In every case of “find (X finds Y)” as described above, X is "
     "the one that does the finding — someone or something that can "
     "look for things or come upon them; not a time or a place.",
  a2="Normally X is a person, or an animal or other being that can "
     "perceive.",
  a3="Typically X was looking for Y, or at least comes to know where Y is."),
 "g2:pi:037": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Discovering", "Object"], fn="Locating", rank="moderate",
  a1="In every case of “find (X finds Y)” as described above, Y is "
     "what is found — something that was not in view, or not known to "
     "be where it is, and then is.",
  a2="Normally Y is a thing, but it can be a person, an animal, a place, "
     "or even something like an answer.",
  a3="Typically Y is somewhere — the finding fixes where it is."),
 # -- forget ----------------------------------------------------------
 "g2:pi:038": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["PsychologicalProcess", "CognitiveAgent"], fn="Memory",
  rank="moderate",
  a1="In every case of “forget (X forgets Y)” as described above, "
     "X is the one who forgets — someone, or some being, that could "
     "know or remember things; not a time, a place, or a mere thing.",
  a2="Normally X is a person or other thinking being.",
  a3="Typically Y was in X’s mind before, and is not there when it is "
     "wanted."),
 "g2:pi:039": dict(fam="agent-intention-goal",
  bfo="generically dependent continuant",
  sumo=["PsychologicalProcess", "Proposition"], fn="Memory", rank="moderate",
  a1="In every case of “forget (X forgets Y)” as described above, "
     "Y is what is forgotten — something that was known, remembered, "
     "or meant to be done.",
  a2="Normally Y is something that can be held in mind: a fact, a name, a "
     "plan, a happening.",
  a3="Typically Y can also be a person, a thing, or a place, remembered "
     "under some description."),
 # -- friend ----------------------------------------------------------
 "g2:pi:040": dict(fam="role-vs-phase", bfo="material entity",
  sumo=["Human", "SocialInteraction"], fn="Personal_relationship",
  rank="strong",
  a1="In every case of “friend (X is a friend of Y)” as described "
     "above, X is a being one can have a bond with — someone, not a "
     "mere thing, a time, or a place.",
  a2="Normally X is a person; people also speak of animals, or of groups, "
     "as friends.",
  a3="Typically X is one of two or more who like each other and are close."),
 "g2:pi:041": dict(fam="role-vs-phase", bfo="material entity",
  sumo=["Human", "SocialInteraction"], fn="Personal_relationship",
  rank="strong",
  a1="In every case of “friend (X is a friend of Y)” as described "
     "above, Y is a being one can have a bond with — someone, not a "
     "mere thing, a time, or a place.",
  a2="Normally Y is a person; people also speak of animals, or of groups, "
     "as friends.",
  a3="Typically Y is one of two or more who like each other and are close."),
 # -- gift ------------------------------------------------------------
 "g2:pi:043": dict(fam="role-vs-phase", bfo="role",
  sumo=["UnilateralGiving", "Human"], fn="Giving", rank="strong",
  a1="In every case of a gift, there is someone the gift is for — one "
     "meant to have it.",
  a2="Normally someone other than the giver, and the giver wants them to "
     "have it.",
  a3="Typically that one receives it, or is meant to receive it."),
 "g2:pi:044": dict(fam="event-action", bfo="process",
  sumo=["UnilateralGiving"], fn="Giving", rank="strong",
  a1="In every case of a gift, a giving is in play — the gift is "
     "given, or meant to be given.",
  a2="Normally the giving is done freely, with nothing owed for it.",
  a3="Typically there is the giver, the gift itself, and the one it goes "
     "to."),
 # -- give ------------------------------------------------------------
 "g2:pi:045": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["Giving", "AutonomousAgent"], fn="Giving", rank="strong",
  a1="In every case of “give (X gives Y to someone)” as described "
     "above, X is the giver — the one from whom Y goes; someone or "
     "something that can have and hand over.",
  a2="Normally X is a person or a group of people.",
  a3="Typically X has Y first, and after the giving the other one has it."),
 "g2:pi:046": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Giving", "Object"], fn="Giving", rank="strong",
  a1="In every case of “give (X gives Y to someone)” as described "
     "above, Y is what is given — something that can go from one to "
     "another.",
  a2="Normally Y is a thing that can be had or kept.",
  a3="But Y can also be something like help, time, words, or care."),
 "g2:pi:047": dict(fam="event-action", bfo="temporal region",
  sumo=["Giving", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of “give (X gives Y to someone)” as described "
     "above, the giving happens at some time — there is a time at "
     "which it takes place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- grieving --------------------------------------------------------
 "g2:pi:050": dict(fam="quality-vs-disposition", bfo="quality",
  sumo=["EmotionalState"], fn=None, rank="moderate",
  a1="Whenever someone or something is grieving, they feel something very "
     "bad over one that is gone — grieving is a state they are in.",
  a2="Normally the grieving follows a death — of a person or other "
     "loved being — or another deep loss, and the loss came before "
     "the grieving.",
  a3=None),
 # -- has part --------------------------------------------------------
 "g2:pi:051": dict(fam="generic-type-vs-kind", bfo="entity",
  sumo=["part", "Object"], fn="Part_whole", rank="moderate",
  a1="In every case of “has part (X has part Y)” as described "
     "above, X is a whole — something with parts; it can be a thing, a "
     "person, a place, or even a happening.",
  a2="Normally X is one thing whose parts belong to it and make it up.",
  a3="Typically X is more than Y: the whole is not less than the part."),
 "g2:pi:052": dict(fam="generic-type-vs-kind", bfo="entity",
  sumo=["part", "Object"], fn="Part_whole", rank="moderate",
  a1="In every case of “has part (X has part Y)” as described "
     "above, Y is a part — something that belongs to X and helps make "
     "it up; it can be a thing, a person, a place, or even a happening.",
  a2="Normally Y is a smaller piece or portion of the whole.",
  a3="Typically Y is where X is — the part is not somewhere else than "
     "its whole."),
 # -- help ------------------------------------------------------------
 "g2:pi:053": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["AutonomousAgent", "IntentionalProcess"], fn="Assistance",
  rank="strong",
  a1="In every case of “help (X helps Y)” as described above, X is "
     "what does the helping — someone or something that makes things "
     "better or easier for Y.",
  a2="Normally X is a person or other being acting on purpose.",
  a3="But X can also be a thing or a happening that helps — a tool, a "
     "medicine, a change."),
 "g2:pi:054": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Human", "AutonomousAgent"], fn="Assistance", rank="strong",
  a1="In every case of “help (X helps Y)” as described above, Y is "
     "the one helped — someone or something whose doing or situation "
     "the help is for.",
  a2="Normally Y is a person or a group of people.",
  a3="Typically the help goes toward something Y is doing or needs."),
 # -- inside ----------------------------------------------------------
 "g2:pi:056": dict(fam="generic-type-vs-kind", bfo="independent continuant",
  sumo=["Inside", "Object"], fn="Interior_profile_relation", rank="moderate",
  a1="In every case of “inside (X is inside Y)” as described "
     "above, X is something with a place — a thing, a person, or a "
     "stuff that is somewhere; not a time.",
  a2="Normally X is a thing or being that could also be elsewhere.",
  a3="Typically X is surrounded by Y — within it, not at its edge."),
 "g2:pi:057": dict(fam="generic-type-vs-kind", bfo="independent continuant",
  sumo=["Inside", "Object"], fn="Interior_profile_relation", rank="moderate",
  a1="In every case of “inside (X is inside Y)” as described "
     "above, Y is something with an inside — a thing, a place, or a "
     "container that can hold or surround; not a time.",
  a2="Normally Y has bounds — walls, edges, or a surface — with "
     "room within them.",
  a3="Typically Y is bigger than X and around it."),
 # -- kind ------------------------------------------------------------
 "g2:pi:058": dict(fam="generic-type-vs-kind", bfo=None,
  sumo=[], fn=None, rank="underdetermined",
  a1="In every case of a kind, there are — or could be — things "
     "of that kind: a kind is a way things are grouped as being alike.",
  a2=None, a3=None),
 # -- learn -----------------------------------------------------------
 "g2:pi:059": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["Learning", "CognitiveAgent"], fn="Education_teaching", rank="strong",
  a1="In every case of “learn (X learns Y)” as described above, X "
     "is the learner — someone or something that can come to know; not "
     "a time, a place, or a mere thing.",
  a2="Normally X is a person or other being with a mind — an animal "
     "can learn too.",
  a3="Typically after the learning, X knows Y or can do Y."),
 "g2:pi:060": dict(fam="agent-intention-goal",
  bfo="generically dependent continuant",
  sumo=["Learning", "Proposition"], fn="Education_teaching", rank="strong",
  a1="In every case of “learn (X learns Y)” as described above, Y "
     "is what is learned — something that can be known or done: a "
     "fact, a skill, a way.",
  a2="Normally Y is content one can carry in mind — knowledge or "
     "know-how.",
  a3="Typically Y can be about anything — persons, places, things, "
     "happenings."),
 # -- lie -------------------------------------------------------------
 "g2:pi:062": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["Stating", "LinguisticCommunication"], fn="Prevarication",
  rank="strong",
  a1="Every lie is something said — made of words, spoken or written.",
  a2="Normally the words say something the one saying them takes to be "
     "not true.",
  a3="Typically it is said to someone, about something."),
 "g2:pi:063": dict(fam="role-vs-phase", bfo="role",
  sumo=["Stating", "Human"], fn="Prevarication", rank="strong",
  a1="In every case of a lie, the words are said to someone — a lie is "
     "told.",
  a2="Normally to someone else — though one can, in a stretched way, "
     "lie to oneself.",
  a3="Typically the teller wants the one told to take the words as true."),
 "g2:pi:064": dict(fam="role-vs-phase", bfo="role",
  sumo=["Stating", "Human"], fn="Prevarication", rank="strong",
  a1="In every case of a lie, someone tells it — there is the one "
     "whose words they are.",
  a2="Normally a person speaking or writing.",
  a3="Typically the teller knows the words are not true."),
 # -- lose ------------------------------------------------------------
 "g2:pi:065": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["ChangeOfPossession", "Human"], fn="Losing", rank="moderate",
  a1="In every case of “lose (X loses Y)” as described above, X is "
     "the one who loses — someone or something that had Y and then "
     "does not.",
  a2="Normally X is a person, or a group, to whom Y belonged or mattered.",
  a3="Typically X can no longer find Y, or no longer has it."),
 "g2:pi:066": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["ChangeOfPossession", "Object"], fn="Losing", rank="moderate",
  a1="In every case of “lose (X loses Y)” as described above, Y is "
     "what is lost — something X had, held, or kept.",
  a2="Normally Y is a thing that can be had — but it can also be a "
     "person kept track of, or something like time, a game, or a way.",
  a3="Typically after the losing, X does not know where Y is, or no "
     "longer has it."),
 # -- lost ------------------------------------------------------------
 "g2:pi:068": dict(fam="quality-vs-disposition", bfo="quality",
  sumo=["ChangeOfPossession", "Attribute"], fn="Losing_track_of_perceiver",
  rank="moderate",
  a1="Whenever someone or something is lost, being lost is how things now "
     "stand with it — it cannot be found by, or does not know its way "
     "to, those it matters to.",
  a2="Normally this came about through an earlier losing — someone "
     "lost it, or it lost its way.",
  a3="Typically no one who matters to it knows where it is."),
 # -- make ------------------------------------------------------------
 "g2:pi:069": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Making", "AutonomousAgent"], fn="Creating", rank="strong",
  a1="In every case of “make (X makes Y)” as described above, X is "
     "the maker — what brings Y into being; someone or something.",
  a2="Normally X is a person, or people, working on purpose.",
  a3="But X can also be a tool, a machine, or a happening in the world "
     "that makes something."),
 "g2:pi:070": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Making", "Artifact"], fn="Creating", rank="strong",
  a1="In every case of “make (X makes Y)” as described above, Y is "
     "what is made — something that comes to be through the making.",
  a2="Normally Y is a thing one can point to afterwards — an object, "
     "a stuff, a work.",
  a3="But Y can also be words, a plan, or a happening — one can make "
     "a promise, or make trouble."),
 "g2:pi:071": dict(fam="event-action", bfo="temporal region",
  sumo=["Making", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of “make (X makes Y)” as described above, the "
     "making happens at some time — there is a time at which it takes "
     "place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- maker of --------------------------------------------------------
 "g2:pi:073": dict(fam="role-vs-phase", bfo="entity",
  sumo=["Making", "Human"], fn="Manufacturing", rank="moderate",
  a1="In every case of “maker of (X is the maker of Y)” as "
     "described above, X is the maker of Y — the one that brought Y "
     "into being.",
  a2="Normally X is a person or people.",
  a3="But a maker can also be a firm, a machine, or nature at work."),
 "g2:pi:074": dict(fam="role-vs-phase", bfo="entity",
  sumo=["Making", "Artifact"], fn="Manufacturing", rank="moderate",
  a1="In every case of “maker of (X is the maker of Y)” as "
     "described above, Y is what was made — something that came to be "
     "through X’s making.",
  a2="Normally Y is a thing one can point to — an object, a stuff, a "
     "work.",
  a3="But Y can also be words, a plan, or a happening that X brought "
     "about."),
 "g2:pi:075": dict(fam="event-action", bfo="process",
  sumo=["Making"], fn="Creating", rank="strong",
  a1="In every case of “maker of (X is the maker of Y)” as "
     "described above, a making happened — Y came to be through it, at "
     "some time.",
  a2="Normally the making was done by X on purpose.",
  a3="Typically the making came before Y’s being there."),
 # -- memory ----------------------------------------------------------
 "g2:pi:077": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["Proposition", "StateOfMind"], fn="Memory", rank="moderate",
  a1="In every case of a memory, the memory is of something — there is "
     "something it keeps or is about.",
  a2="Normally something from before — a happening, a person, a place, "
     "a fact — as it was taken in.",
  a3="Typically the one whose memory it is can bring that content back to "
     "mind."),
 # -- near ------------------------------------------------------------
 "g2:pi:078": dict(fam="generic-type-vs-kind", bfo="independent continuant",
  sumo=["Near", "Object"], fn="Gradable_proximity", rank="moderate",
  a1="In every case of “near (X is near Y)” as described above, X "
     "is something with a place — a thing, a person, or a place "
     "itself; not a time.",
  a2="Normally X is a thing or being located somewhere.",
  a3="Typically the distance between X and Y is small, as such things go."),
 "g2:pi:079": dict(fam="generic-type-vs-kind", bfo="independent continuant",
  sumo=["Near", "Object"], fn="Gradable_proximity", rank="moderate",
  a1="In every case of “near (X is near Y)” as described above, Y "
     "is something with a place — a thing, a person, or a place "
     "itself; not a time.",
  a2="Normally Y is a thing, a being, or a spot that other things can be "
     "close to.",
  a3="Typically the distance between X and Y is small, as such things go."),
 # -- part of ---------------------------------------------------------
 "g2:pi:080": dict(fam="generic-type-vs-kind", bfo="entity",
  sumo=["part", "Object"], fn="Part_whole", rank="moderate",
  a1="In every case of “part of (X is part of Y)” as described "
     "above, X is a part — something that belongs to Y and helps make "
     "it up; it can be a thing, a person, a place, or even a happening.",
  a2="Normally X is a smaller piece or portion of the whole.",
  a3="Typically X is where Y is — the part is not somewhere else than "
     "its whole."),
 "g2:pi:081": dict(fam="generic-type-vs-kind", bfo="entity",
  sumo=["part", "Object"], fn="Part_whole", rank="moderate",
  a1="In every case of “part of (X is part of Y)” as described "
     "above, Y is a whole — something the part belongs to; it can be a "
     "thing, a person, a place, or even a happening.",
  a2="Normally Y is one thing whose parts belong to it and make it up.",
  a3="Typically Y is not less than X: the whole is at least its part."),
 # -- promise ---------------------------------------------------------
 "g2:pi:082": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["Committing", "Promise"], fn="Commitment", rank="strong",
  a1="Every promise is something said — made of words, spoken, "
     "written, or clearly signalled.",
  a2="Normally the words bind the one saying them to do, or not do, "
     "something.",
  a3="Typically it is given to someone, about something to come."),
 "g2:pi:083": dict(fam="role-vs-phase", bfo="role",
  sumo=["Committing", "Human"], fn="Commitment", rank="strong",
  a1="In every case of a promise, it is made to someone — there is one "
     "to whom the word is given.",
  a2="Normally someone else; one can also promise oneself.",
  a3="Typically the one promised can then count on the thing promised."),
 "g2:pi:084": dict(fam="role-vs-phase", bfo="role",
  sumo=["Committing", "Human"], fn="Commitment", rank="strong",
  a1="In every case of a promise, someone makes it — there is the one "
     "who gives their word.",
  a2="Normally a person, or a group speaking as one.",
  a3="Typically the maker of the promise is then bound by it."),
 # -- remember --------------------------------------------------------
 "g2:pi:085": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["Remembering", "CognitiveAgent"], fn="Remembering_information",
  rank="strong",
  a1="In every case of “remember (X remembers Y)” as described "
     "above, X is the one who remembers — someone, or some being, in "
     "whose mind Y is kept or comes back; not a time, a place, or a mere "
     "thing.",
  a2="Normally X is a person or other being with a mind.",
  a3="Typically Y was known to X, or lived through by X, before."),
 "g2:pi:086": dict(fam="agent-intention-goal",
  bfo="generically dependent continuant",
  sumo=["Remembering", "Proposition"], fn="Remembering_information",
  rank="strong",
  a1="In every case of “remember (X remembers Y)” as described "
     "above, Y is what is remembered — something that can be held in "
     "mind: a fact, a happening, a person, a place, a thing to do.",
  a2="Normally Y is content from before — something X knew, saw, or "
     "went through.",
  a3="Typically Y comes back to X’s mind as it was taken in."),
 # -- reminder --------------------------------------------------------
 "g2:pi:089": dict(fam="agent-intention-goal", bfo="process",
  sumo=["IntentionalProcess"], fn="Evoking", rank="moderate",
  a1="In every case of a reminder, it was made or set up — something "
     "was done so that someone will call something back to mind.",
  a2="Normally by someone — a person — often through a tool or "
     "device that then does the reminding.",
  a3="Typically there is the one to be reminded, and the thing to be "
     "brought back to mind."),
 "g2:pi:090": dict(fam="generic-type-vs-kind",
  bfo="generically dependent continuant",
  sumo=["Proposition"], fn="Evoking", rank="strong",
  a1="In every case of a reminder, there is something it is meant to bring "
     "back to mind — the reminder is about, or for, something else.",
  a2="Normally something to be done, or something not to be forgotten.",
  a3="Typically that something is distinct from the reminder itself."),
 # -- repair ----------------------------------------------------------
 "g2:pi:092": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Repairing", "Human"], fn="Rejuvenation", rank="strong",
  a1="In every case of “repair (X repairs Y)” as described above, "
     "X is the one that does the repairing — someone or something that "
     "works on Y so that it is right again.",
  a2="Normally X is a person, or people, with the needed skill.",
  a3="Sometimes X is a tool, a machine, or even the body itself doing the "
     "mending."),
 "g2:pi:093": dict(fam="agent-intention-goal", bfo="material entity",
  sumo=["Repairing", "Artifact"], fn="Rejuvenation", rank="strong",
  a1="In every case of “repair (X repairs Y)” as described above, "
     "Y is what is repaired — a thing that was working or whole, then "
     "was not, and is worked on to be so again.",
  a2="Normally Y is a made thing — something built or put together "
     "that can go wrong.",
  a3="Typically after a good repair, Y works or holds together again."),
 "g2:pi:094": dict(fam="event-action", bfo="temporal region",
  sumo=["Repairing", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of “repair (X repairs Y)” as described above, "
     "the repairing happens at some time — there is a time at which it "
     "takes place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
 # -- take ------------------------------------------------------------
 "g2:pi:095": dict(fam="agent-intention-goal", bfo="independent continuant",
  sumo=["Getting", "AutonomousAgent"], fn="Taking", rank="strong",
  a1="In every case of “take (X takes Y)” as described above, X is "
     "the taker — the one that comes to have or hold Y; someone or "
     "something that can do so.",
  a2="Normally X is a person or other living being.",
  a3="Typically X takes Y from somewhere, or from someone."),
 "g2:pi:096": dict(fam="agent-intention-goal", bfo="entity",
  sumo=["Getting", "Object"], fn="Taking", rank="strong",
  a1="In every case of “take (X takes Y)” as described above, Y is "
     "what is taken — something that can be had, held, or carried off.",
  a2="Normally Y is a thing; it can also be a person led along, or "
     "something like time or a chance.",
  a3="Typically Y comes from somewhere — a place, or someone who had "
     "it."),
 "g2:pi:097": dict(fam="event-action", bfo="temporal region",
  sumo=["Getting", "TimePoint"], fn="Event", rank="strong",
  a1="In every case of “take (X takes Y)” as described above, the "
     "taking happens at some time — there is a time at which it takes "
     "place.",
  a2="Normally one can say when it happened, at least roughly.", a3=None),
}

# Fix the two template-built entries whose a1 used the helper above.
BRIDGE["g2:pi:006"]["a1"] = ("In every case of a birth, it happens at some "
                             "time — there is a time at which the birth "
                             "takes place.")
BRIDGE["g2:pi:006"]["a2"] = ("Normally one can say when it happened, at "
                             "least roughly.")

# FrameNet frame-name -> nothing hardcoded: resolved from frames.jsonl.
# SUMO term names resolved from terms.jsonl. BFO labels from bfo.jsonl.

# deranged-sort glosses for probes, keyed by the slot's true BFO anchor
DERANGE = {
    "occurrent": "a place — somewhere one can be; normally a large place",
    "process": "a place — somewhere one can be; normally a large place",
    "temporal region": "a place — somewhere one can be; normally a "
                       "place far away",
    "independent continuant": "a time — a moment or stretch of time; "
                              "normally a time long past",
    "material entity": "a time — a moment or stretch of time; normally "
                       "a time long past",
    "continuant": "a time — a moment or stretch of time; normally a "
                  "time long past",
    "generically dependent continuant": "a place — somewhere one can "
                                        "be; normally a place far away",
    "quality": "a time — a moment or stretch of time; normally about "
               "an hour long",
    "role": "a time — a moment or stretch of time; normally about an "
            "hour long",
    "entity": "a time — a moment or stretch of time; normally a time "
              "long past",
    None: "a time — a moment or stretch of time; normally a time long "
          "past",
}

FORBIDDEN_EFFECTS = ["assert-type", "reject-world", "derive-disjointness",
                     "mint-entity", "close-domain"]
HARD_LAW_MARKERS = ["rdfs:domain", "rdfs:range", "owl:disjointWith",
                    "owl:someValuesFrom", "owl:Restriction"]


def main():
    # 1. verify pins (plan section 2; fail closed)
    pin_report = {}
    for rel, want in PINS.items():
        p = os.path.join(REPO, rel)
        got = sha_file(p)
        if got != want:
            die("ERR_ONT_PIN: %s sha %s != pinned %s" % (rel, got, want))
        pin_report[rel] = got
    align_pins = {k: sha_file(os.path.join(REPO, v))
                  for k, v in ALIGN_FILES.items()}

    # 2. load sources
    bfo_rows = jload(os.path.join(REPO, "data/onto-obo/bfo.jsonl"))
    bfo_by_label = {r["annotations"]["label"]: r for r in bfo_rows}
    sumo_ids = set()
    for l in open(os.path.join(REPO, "data/onto-sumo/terms.jsonl"),
                  encoding="utf-8"):
        sumo_ids.add(json.loads(l)["id"])
    fn_by_frame = {}
    for l in open(os.path.join(REPO, "data/onto-framenet/frames.jsonl"),
                  encoding="utf-8"):
        r = json.loads(l)
        fn_by_frame[r["frame"]] = {
            "id": r["id"],
            "coreFEs": [fe["name"] for fe in r["frameElements"]
                        if fe["coreType"] == "Core"]}
    items = jload(os.path.join(REPO, "poc/g2/materials/items.jsonl"))
    labels_a0 = {r["id"]: r for r in
                 jload(os.path.join(REPO, "poc/g2/labels-proxy.jsonl"))}
    aligns = {k: json.load(open(os.path.join(REPO, v), encoding="utf-8"))
              for k, v in ALIGN_FILES.items()}

    if len(items) != 84:
        die("ERR_ONT_SLOTS: %d items != 84" % len(items))
    ids = [it["id"] for it in items]
    if sorted(BRIDGE) != sorted(ids):
        missing = sorted(set(ids) - set(BRIDGE))
        extra = sorted(set(BRIDGE) - set(ids))
        die("ERR_ONT_SLOTS: bridge table mismatch missing=%s extra=%s"
            % (missing, extra))

    # alignment lookup: concept urn -> {source: [target urns]}
    def aligned_targets(subject, source):
        return [a["to"] for a in aligns[source]["alignments"]
                if a["from"] == subject]

    # 3. compile bridge + soft-type records, render arms
    bridge_out, soft_out, conflicts, anchor_out = [], [], [], []
    arm_rows = {"a1": [], "a2": [], "a3": []}
    a0_rows = []
    vac = {"a1": {}, "a2": {}, "a3": {}}
    depth_cache = {}

    def bfo_depth(label):
        if label in depth_cache:
            return depth_cache[label]
        d, cur = 0, bfo_by_label[label]
        by_id = {r["id"]: r for r in bfo_rows}
        while True:
            isa = [a["target"] for a in cur.get("axioms", [])
                   if a["rel"] == "is_a"]
            if not isa:
                break
            cur = by_id[isa[0]]
            d += 1
        depth_cache[label] = d
        return d

    for lab, r in sorted(bfo_by_label.items()):
        anchor_out.append({"id": r["id"], "label": lab,
                           "depth": bfo_depth(lab),
                           "is_a": [a["target"] for a in r.get("axioms", [])
                                    if a["rel"] == "is_a"]})

    for it in items:
        iid, subj = it["id"], it["subject"]
        b = BRIDGE[iid]
        # resolve targets, fail closed
        bfo_urn = bfo_lab = None
        if b["bfo"] is not None:
            if b["bfo"] not in bfo_by_label:
                die("ERR_ONT_URN: BFO label %r (%s)" % (b["bfo"], iid))
            bfo_urn = bfo_by_label[b["bfo"]]["id"]
            bfo_lab = b["bfo"]
        sumo_urns = []
        for t in b["sumo"]:
            u = "urn:onto-sumo:%s" % t
            if u not in sumo_ids:
                die("ERR_ONT_URN: SUMO term %r (%s)" % (t, iid))
            sumo_urns.append(u)
        fn_ref = None
        if b["fn"] is not None:
            if b["fn"] not in fn_by_frame:
                die("ERR_ONT_URN: FrameNet frame %r (%s)" % (b["fn"], iid))
            fn_ref = dict(fn_by_frame[b["fn"]], frame=b["fn"])
        # alignment-consistency: cited targets must include any frozen
        # alignment link for this concept when one exists in that source
        al_notes = {}
        for src, targets in (("sumo", sumo_urns),
                             ("framenet", [fn_ref["id"]] if fn_ref else [])):
            frozen = aligned_targets(subj, src)
            if frozen:
                hit = any(t in targets for t in frozen)
                al_notes[src] = {"frozen": frozen, "cited": hit}
                if not hit and targets:
                    conflicts.append({
                        "id": iid, "source": src, "kind": "alignment-divergence",
                        "frozen": frozen, "cited": targets,
                        "note": "bridge cites a different %s target than the "
                                "frozen alignment; recorded, not resolved "
                                "(plan section 4.4: conflict never resolves "
                                "by narrowing)" % src})
        # vacuity per arm (plan section 7.3 operationalisation, ASM row):
        # non-vacuous iff BFO anchor strictly below `entity` OR a
        # source-specific SUMO/FrameNet preference is present in that arm
        below_entity = bfo_lab is not None and bfo_lab != "entity"
        vac["a1"][iid] = not below_entity
        vac["a2"][iid] = not (below_entity or bool(sumo_urns))
        vac["a3"][iid] = not (below_entity or bool(sumo_urns) or bool(fn_ref))
        if b["bfo"] is None or b["rank"] == "underdetermined":
            conflicts.append({
                "id": iid, "source": "bfo", "kind": "underdetermined",
                "alternatives": aligned_targets(subj, "obo"),
                "note": "no BFO anchor endorsed (plan section 5.3: no BFO "
                        "equivalent of gUFO Kind; generic-type recorded with "
                        "unresolved future_gufo_target)"})
        # bridge candidate (kot-ont-bridge/1)
        bridge_rec = {
            "schema": SCHEMA_BRIDGE,
            "id": "urn:kot-ont-bridge:g2i:%s" % iid.replace(":", "-"),
            "concept": subj,
            "slot": {"g2_item": iid, "rule": it["rule"], "form": it["form"]},
            "target": ({"ontology": "bfo", "id": bfo_urn, "label": bfo_lab}
                       if bfo_urn else None),
            "relation": ("supportedClassification" if bfo_urn
                         else "underdetermined"),
            "status": ("experiment-only" if bfo_urn else "underdetermined"),
            "strength": b["rank"],
            "pattern_family": b["fam"],
            "warrant": {
                "imported_evidence":
                    [{"source": "sumo", "ref": u} for u in sumo_urns]
                    + ([{"source": "framenet", "ref": fn_ref["id"],
                         "core_fes": fn_ref["coreFEs"]}] if fn_ref else []),
                "alignment_notes": al_notes,
            },
            "additional_commitments": [],
            "counterevidence": [],
            "identity_bearing": False,
            "authority": "candidate",
            "review": {"author": "experiment-designer-role",
                       "endorsers": []},
            "provenance": {"build": "ontg2/1", "date": BUILD_DATE},
        }
        bridge_out.append(bridge_rec)
        # soft-type record (kot-soft-type/1)
        soft_rec = {
            "schema": SCHEMA_SOFT,
            "id": "urn:kot-soft-type:g2i:%s" % iid.replace(":", "-"),
            "concept": subj,
            "position": {"rule_family": it["rule"], "form": it["form"],
                         "g2_item": iid},
            "preferred_type": {
                "anchor": bfo_urn, "label": bfo_lab,
                "source_specific": sumo_urns
                                   + ([fn_ref["id"]] if fn_ref else []),
            },
            "strength": "preference",
            "binding": False,
            "regime": "policy",
            "authority": "preference",
            "effect": "rank-only",
            "evidence": {"bridge_refs": [bridge_rec["id"]],
                         "source_pins": pin_report},
            "forbidden_effects": FORBIDDEN_EFFECTS,
            "vacuous_by_arm": {k: vac[k][iid] for k in ("a1", "a2", "a3")},
        }
        soft_out.append(soft_rec)
        # rendered arms: monotone A1 <= A2 <= A3 (evidence-gated clauses)
        header = it["item"].split("\nStatement:")[0]
        s1 = b["a1"]
        s2 = s1 + ((" " + b["a2"]) if (b["a2"] and sumo_urns) else "")
        s3 = s2 + ((" " + b["a3"]) if (b["a3"] and fn_ref) else "")
        for arm, stmt in (("a1", s1), ("a2", s2), ("a3", s3)):
            for marker in HARD_LAW_MARKERS:
                if marker in stmt:
                    die("ERR_ONT_HARDLAW: %s in %s/%s" % (marker, arm, iid))
            arm_rows[arm].append({
                "id": iid, "rule": it["rule"], "form": it["form"],
                "subject": subj, "arm": arm.upper(),
                "item": "%s\nStatement: %s" % (header, stmt)})
        a0_rows.append({
            "id": iid, "rule": it["rule"], "form": it["form"],
            "subject": subj, "arm": "A0", "item": it["item"],
            "answer_pA_frozen": labels_a0[iid]["answer_pA"],
            "answer_pB_frozen": labels_a0[iid]["answer_pB"]})

    # 4. probes: 20 per arm, deranged-sort with soft hedges kept
    probes = {}
    for arm in ("a1", "a2", "a3"):
        order = sorted(ids, key=lambda i: sha_str("ontg2-probe/1|%s|%s"
                                                  % (arm, i)))
        chosen = order[:20]
        rows = []
        for k, iid in enumerate(chosen):
            it = next(x for x in items if x["id"] == iid)
            b = BRIDGE[iid]
            header = it["item"].split("\nStatement:")[0]
            gloss = DERANGE[b["bfo"]]
            if it["form"] == "subClassOf":
                word = header.split("“")[1].split("”")[0].split(" (")[0]
                stmt = "Every %s is %s." % (word, gloss)
            elif it["form"] in ("domain", "range"):
                var = "X" if it["form"] == "domain" else \
                      ("T" if "time T" in header else "Y")
                mid = header.split("“")[1].split("”")[0]
                stmt = ("In every case of “%s” as described above, "
                        "%s is %s." % (mid, var, gloss))
            else:  # existential
                mid = header.split("“")[1].split("”")[0]
                stmt = ("In every case of “%s”, there is a place that "
                        "makes it happen on purpose — normally a place "
                        "far away." % mid)
            rows.append({"id": "ontg2:probe:%s:%03d" % (arm, k),
                         "source_id": iid, "arm": arm.upper(),
                         "rule": it["rule"], "form": it["form"],
                         "expected": "no",
                         "item": "%s\nStatement: %s" % (header, stmt)})
        probes[arm] = rows

    # 5. write outputs
    os.makedirs(OUT_DATA, exist_ok=True)
    os.makedirs(OUT_POC, exist_ok=True)

    def wjsonl(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(jdump_line(r))
        return sha_file(path)

    shas = {}
    shas["bfo-anchor.jsonl"] = wjsonl(
        os.path.join(OUT_DATA, "bfo-anchor.jsonl"), anchor_out)
    shas["bridge-candidates.jsonl"] = wjsonl(
        os.path.join(OUT_DATA, "bridge-candidates.jsonl"), bridge_out)
    shas["soft-type-candidates.jsonl"] = wjsonl(
        os.path.join(OUT_DATA, "soft-type-candidates.jsonl"), soft_out)
    shas["conflicts.jsonl"] = wjsonl(
        os.path.join(OUT_DATA, "conflicts.jsonl"), conflicts)

    attribution = {
        "bfo": {"license": "CC BY 4.0",
                "source": "Basic Formal Ontology (OBO Foundry canonical "
                          "serialization)",
                "pin": pin_report["data/onto-obo/bfo.jsonl"]},
        "sumo": {"license": "IEEE redistribution terms as recorded in "
                            "data/onto-sumo/manifest.json",
                 "source": "SUMO Merge+MILO",
                 "pin": pin_report["data/onto-sumo/terms.jsonl"]},
        "framenet": {"license": "CC BY 3.0",
                     "source": "FrameNet 1.7 frame metadata (NOT the "
                               "annotated sentence corpus)",
                     "pin": pin_report["data/onto-framenet/frames.jsonl"]},
        "note": "record-level provenance rides every bridge/soft record; "
                "this file is the shard-level attribution required by plan "
                "section 2.",
    }
    with open(os.path.join(OUT_DATA, "source-attribution.json"), "w") as f:
        f.write(json.dumps(attribution, indent=1, sort_keys=True) + "\n")
    shas["source-attribution.json"] = sha_file(
        os.path.join(OUT_DATA, "source-attribution.json"))

    # arms
    arm_files = {}
    arm_files["arm-a0-baseline.jsonl"] = wjsonl(
        os.path.join(OUT_POC, "arm-a0-baseline.jsonl"), a0_rows)
    arm_files["arm-a1-bfo.jsonl"] = wjsonl(
        os.path.join(OUT_POC, "arm-a1-bfo.jsonl"), arm_rows["a1"])
    arm_files["arm-a2-bfo-sumo.jsonl"] = wjsonl(
        os.path.join(OUT_POC, "arm-a2-bfo-sumo.jsonl"), arm_rows["a2"])
    arm_files["arm-a3-bfo-sumo-framenet.jsonl"] = wjsonl(
        os.path.join(OUT_POC, "arm-a3-bfo-sumo-framenet.jsonl"),
        arm_rows["a3"])
    for arm in ("a1", "a2", "a3"):
        arm_files["probes-%s.jsonl" % arm] = wjsonl(
            os.path.join(OUT_POC, "probes-%s.jsonl" % arm), probes[arm])

    # order-seed manifest (fresh seeds; sort-by-sha rule as run-g2lp.py)
    seeds, orders = {}, {}
    for pk in ("pA", "pB"):
        for arm in ("a1", "a2", "a3"):
            for phase, idset in (("real", ids),
                                 ("probe", [p["id"] for p in probes[arm]])):
                key = "judge-%s|%s|%s" % (pk, arm, phase)
                seed = "ontg2/1|%s|%s" % (key, BUILD_DATE)
                seeds[key] = seed
                orders[key] = sorted(
                    idset, key=lambda i: sha_str("%s|%s" % (seed, i)))
    mat_manifest = {
        "schema": "ontg2-materials/1",
        "build_date": BUILD_DATE,
        "order_rule": "sorted(ids, key=sha256(seed|id)) — the "
                      "run-g2lp.py::_run_block rule, fresh seeds",
        "seeds": seeds, "orders": orders,
        "n_real": 84, "n_probe_per_arm": 20,
        "calibration": "poc/g2/materials/calibration-items.jsonl (reused, "
                       "pinned by the harness)",
    }
    with open(os.path.join(OUT_POC, "manifest.json"), "w") as f:
        f.write(json.dumps(mat_manifest, indent=1, sort_keys=True) + "\n")
    arm_files["manifest.json"] = sha_file(os.path.join(OUT_POC,
                                                       "manifest.json"))

    # generation report (plan section 6)
    by_rule = {"R1": 0, "R3": 0, "R4": 0}
    for it in items:
        by_rule[it["rule"]] += 1
    nonvac = {arm: sum(1 for iid in ids if not vac[arm][iid])
              for arm in ("a1", "a2", "a3")}
    nonvac_r3 = {arm: sum(1 for it in items
                          if it["rule"] == "R3" and not vac[arm][it["id"]])
                 for arm in ("a1", "a2", "a3")}
    depth_dist = {}
    for iid in ids:
        lab = BRIDGE[iid]["bfo"]
        d = "none" if lab is None else str(bfo_depth(lab))
        depth_dist[d] = depth_dist.get(d, 0) + 1
    src_contrib = {
        "bfo_only": sum(1 for iid in ids if BRIDGE[iid]["bfo"] and
                        not BRIDGE[iid]["sumo"] and not BRIDGE[iid]["fn"]),
        "with_sumo": sum(1 for iid in ids if BRIDGE[iid]["sumo"]),
        "with_framenet": sum(1 for iid in ids if BRIDGE[iid]["fn"]),
        "sumo_and_framenet": sum(1 for iid in ids
                                 if BRIDGE[iid]["sumo"] and BRIDGE[iid]["fn"]),
        "underdetermined": sum(1 for iid in ids
                               if BRIDGE[iid]["rank"] == "underdetermined"),
    }
    fam_dist = {}
    for iid in ids:
        fam_dist[BRIDGE[iid]["fam"]] = fam_dist.get(BRIDGE[iid]["fam"], 0) + 1
    report = {
        "schema": "ontg2-generation-report/1",
        "n_input_slots": 84,
        "n_output_slots_per_arm": {a: len(arm_rows[a]) for a in arm_rows},
        "slots_by_rule": by_rule,
        "non_vacuous_by_arm": nonvac,
        "non_vacuous_r3_by_arm": nonvac_r3,
        "informativeness_guard": {"a3_required": 67, "a3_r3_required": 34,
                                  "a3_actual": nonvac["a3"],
                                  "a3_r3_actual": nonvac_r3["a3"]},
        "bfo_depth_distribution": depth_dist,
        "source_contribution": src_contrib,
        "pattern_families": fam_dist,
        "n_conflicts": len(conflicts),
        "hard_operational_axioms_emitted": 0,
        "forbidden_effects_check": "PASS (every soft record carries "
                                   "binding:false effect:rank-only; zero "
                                   "hard-law markers in any rendering)",
    }
    with open(os.path.join(OUT_POC, "generation-report.json"), "w") as f:
        f.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    arm_files["generation-report.json"] = sha_file(
        os.path.join(OUT_POC, "generation-report.json"))

    # validators (fail closed)
    for arm in ("a1", "a2", "a3"):
        got = [r["id"] for r in arm_rows[arm]]
        if got != ids:
            die("ERR_ONT_SLOTS: arm %s id drift" % arm)
    for rec in soft_out:
        if rec["binding"] is not False or rec["effect"] != "rank-only" \
                or rec["regime"] != "policy":
            die("ERR_ONT_SOFT: record %s not non-binding" % rec["id"])
        if sorted(rec["forbidden_effects"]) != sorted(FORBIDDEN_EFFECTS):
            die("ERR_ONT_SOFT: record %s forbidden_effects" % rec["id"])
    for rec in bridge_out:
        if rec["identity_bearing"] is not False or \
                rec["authority"] != "candidate":
            die("ERR_ONT_BRIDGE: record %s identity/authority" % rec["id"])
    if nonvac["a3"] < 67 or nonvac_r3["a3"] < 34:
        # This is a BUILD lint, not the experiment gate: it flags at build
        # time that the informativeness guard would fail before any spend.
        die("ERR_ONT_VACUITY: A3 non-vacuous %d/84 (need 67) R3 %d/42 "
            "(need 34)" % (nonvac["a3"], nonvac_r3["a3"]))

    # MAPPING.md (the mapping doc; deterministic render of the table)
    md = []
    md.append("# onto-softtype: the ONT-TYPE-G2/1 imported SOFT-typing "
              "layer (mapping doc)\n")
    md.append("**Build:** `poc/ontology-import-g2/build-softtype.py` "
              "(deterministic; date constant %s)  " % BUILD_DATE)
    md.append("**Plan:** `docs/next/design/ontology-import-plan.md` "
              "(maintainer-approved direction, issue #20)  ")
    md.append("**Status:** EXPERIMENT-ONLY candidates. Nothing here is "
              "endorsed; `binding:false`, `effect:rank-only`, "
              "`identity_bearing:false` on every record. SOFT expectations "
              "only — never hard laws; never part of any concept hash.\n")
    md.append("## What this fixes\n")
    md.append("The g2 readout scored the hand-authored HARD 4-sort scheme "
              "(Person/Thing/Place/Time universals) at 33/84 = 0.39 "
              "soundness under the directive-#11 proxy protocol: hard "
              "universal typing over-constrains ordinary meaning (e.g. "
              "“X breaks Y ⇒ X is a person” fails on storms; "
              "“Y is a thing, not a person” fails on finding a "
              "person). This layer replaces each hard universal with (i) a "
              "broad BFO-anchored claim that ordinary meaning does "
              "guarantee, plus (ii) explicitly SOFT selectional preferences "
              "(“normally…”, SUMO-backed) and (iii) valency "
              "expectations (“typically…”, FrameNet-backed). "
              "Arms: A1 = BFO anchor only (breadth control), A2 = +SUMO, "
              "A3 = +SUMO+FrameNet (intended adoption arm).\n")
    md.append("## Vacuity rule (operationalised)\n")
    md.append("A slot is NON-vacuous in an arm iff its BFO anchor is "
              "strictly below `entity` OR a source-specific SUMO/FrameNet "
              "preference is present in that arm. Vacuous slots score 0 "
              "regardless of the judge label (plan §7.3). Counts this "
              "build: A1 %d/84, A2 %d/84, A3 %d/84 non-vacuous (R3: %d/42 "
              "at A3).\n" % (nonvac["a1"], nonvac["a2"], nonvac["a3"],
                             nonvac_r3["a3"]))
    md.append("## Per-slot mapping\n")
    md.append("| slot | concept | rule/form | family | BFO anchor | SUMO "
              "evidence | FrameNet evidence (Core FEs) | rank |")
    md.append("|---|---|---|---|---|---|---|---|")
    for it in items:
        b = BRIDGE[it["id"]]
        fnc = ""
        if b["fn"]:
            fnc = "%s (%s)" % (b["fn"],
                               ", ".join(fn_by_frame[b["fn"]]["coreFEs"][:4]))
        md.append("| %s | %s | %s/%s | %s | %s | %s | %s | %s |" % (
            it["id"], it["subject"].split(":")[-1], it["rule"], it["form"],
            b["fam"], b["bfo"] or "— (underdetermined)",
            ", ".join(b["sumo"]) or "—", fnc or "—", b["rank"]))
    md.append("\n## Forbidden directions (binding)\n")
    md.append("- ontology label → replacement definition → changed "
              "concept meaning/identity: FORBIDDEN (plan §3.1).")
    md.append("- any serialization as operational `rdfs:domain` / "
              "`rdfs:range` / `owl:disjointWith` / existential-generating "
              "rules over kernel or world entities: FORBIDDEN "
              "(plan §3.4); build validator fails closed.")
    md.append("- BFO source-internal disjointness never propagates through "
              "a soft bridge to reject a kernel concept or world instance.")
    md.append("- FrameNet FE names are roles, not ontological types; they "
              "supply valency evidence only.\n")
    md.append("## Files\n")
    md.append("| file | sha256 |")
    md.append("|---|---|")
    for k in sorted(shas):
        md.append("| %s | %s |" % (k, shas[k]))
    with open(os.path.join(OUT_DATA, "MAPPING.md"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    shas["MAPPING.md"] = sha_file(os.path.join(OUT_DATA, "MAPPING.md"))

    manifest = {
        "schema": "onto-softtype-manifest/1",
        "build": "ontg2/1",
        "build_date": BUILD_DATE,
        "builder": "poc/ontology-import-g2/build-softtype.py",
        "plan": "docs/next/design/ontology-import-plan.md",
        "path_note": "task-directed path data/onto-softtype/ carrying the "
                     "plan section-6 artifact list (plan's provisional name "
                     "was data/ontology-import-v0/)",
        "input_pins": pin_report,
        "alignment_pins": align_pins,
        "outputs": shas,
        "arm_outputs": arm_files,
        "counts": report,
    }
    with open(os.path.join(OUT_DATA, "manifest.json"), "w") as f:
        f.write(json.dumps(manifest, indent=1, sort_keys=True) + "\n")

    print(json.dumps({"ok": True, "non_vacuous": nonvac,
                      "non_vacuous_r3_a3": nonvac_r3["a3"],
                      "conflicts": len(conflicts),
                      "families": fam_dist}, sort_keys=True))


if __name__ == "__main__":
    main()
