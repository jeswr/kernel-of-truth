#!/usr/bin/env python3
"""NLB-0-A repaired Tier-0 front-end (design-phase DIAGNOSTIC artifact).

Implements the deterministic frame-layer repair of docs/next/design/NLB.md
SS3.1 / SS7.1 [STIPULATED: ASM-0904(2), ASM-0944]:

  (i)  the direction/frame decision is rebuilt from an EXPLICIT per-vertical
       directional-frame inventory (INVENTORY below; exported to
       inventory.json), with a fail-closed rule: any phrasing whose
       orientation/frame cues are ABSENT or CONFLICTING yields NO Tier-0
       parse (refusal), never a defaulted direction or frame;
  (ii) template matching stays exact-match-only: the acceptance set is NOT
       broadened (every phrasing accepted here was accepted by the pinned
       front-end; repairs only correct or refuse previously-accepted items).

The PINNED front-end (tools/experiments/nlb/nlb_frontend.py, sha-pinned in
the frozen l3a-parse / a5-nl records) is IMPORTED, never edited; gazetteer,
mapper bridge, label tables, and text normalisation are reused byte-identical.

Two registered inventory arms (poc-level, diagnostic co-report only):

  inventory-B (PRIMARY, the SS3.1 fail-closed semantics): on the a5
      containment/definition frame-group, the container-ask reading
      ("which scope holds/defines X") has TWO live grammar realisations
      (contained-in, where-defined) whose engine denotations differ by
      construction (lookup list vs unique scalar); no closed surface cue
      discriminates them (measured: DEV and EVAL authors cross the verbs),
      so the reading is EVIDENCE-AMBIGUOUS and Tier-0 REFUSES it.
  inventory-A (ablation, own-label-cue semantics): the op's own surface
      label discriminates ("defined" -> where-defined; "contained/held" ->
      contained-in); refuses only on verb-family conflict. This reproduces
      the pinned front-end's convention minus its cascade-order defects and
      measures how much of S2 that convention leaves alive.

l3a repair (same defect class, measured: 8/8 wrongs are unique->lookup
arity substitutions on imperative-start singular-definite phrasings, zero
direction flips): imperative listing starts ('list/name/find') stop forcing
op=lookup in role shape; the op is decided by the relation head-noun's
grammatical NUMBER (a real surface cue), fail-closed on conflict. Direction
logic (ROLE_DIR x role/flip shape with ambiguous-refuse) is unchanged and is
documented + exhaustively tested as the l3a orientation inventory.

Deterministic; no RNG; CPU only. DIAGNOSTIC LABEL (ASM-0904(4)/ASM-0944(4)):
never a gate arm, never trains on any blind corpus, results can never
substitute for G-NLB; parent-verdict provenance: registry/verdicts/
{l3a-parse,a5-nl}.json (public outcomes).
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "tools", "experiments", "nlb"))

import nlb_frontend as fe  # noqa: E402  (pinned module, imported read-only)

refusal = fe.refusal
_ART = fe._ART

# =====================================================================
# The per-vertical directional-frame inventory (SS7.1 deliverable).
# Every regex operates on the cleaned masked text ('@' = the one entity).
# 'example' fields make the both-orientation unit tests exhaustive over
# the inventory BY CONSTRUCTION (test_orientation.py iterates this table).
# =====================================================================
INVENTORY = {
    "a5": {
        "call": {
            "relation": "code-calls",
            "keyword_gate": r"\b(?:call|calls|called|calling|caller|callers"
                            r"|callee|callees|invoke|invokes|invoked"
                            r"|invoking)\b",
            "orientations": {
                "callees-of": [   # forward: the things @ calls
                    {"pattern": r"\bcalls (?:does|did) @",
                     "example": "what calls does @ make"},
                    {"pattern": r"\b(?:does|did|do) @ (?:call|invoke)",
                     "example": "which routines does @ call"},
                    {"pattern": r"\bcallees of %s@" % _ART,
                     "example": "list the callees of the function @"},
                    {"pattern": r"\b(?:called|invoked) (?:by|from) %s@" % _ART,
                     "example": "which functions are called by @"},
                ],
                "callers-of": [   # inverse: the things that call @
                    {"pattern": r"\bcallers of %s@" % _ART,
                     "example": "list the callers of the function @"},
                    {"pattern": r"@ (?:is|was|get|gets) (?:called|invoked)",
                     "example": "where @ is called"},
                    {"pattern": r"\bcalls to %s@" % _ART,
                     "example": "which functions make calls to @"},
                    {"pattern": r"\b(?:call|calls|invoke|invokes|calling"
                                r"|invoking) %s@" % _ART,
                     "example": "which routines call the function @"},
                ],
            },
        },
        "import": {
            "relation": "code-imports",
            "keyword_gate": r"\b(?:import|imports|imported|importing)\b",
            "orientations": {
                "imports-of": [   # forward: the things @ imports
                    {"pattern": r"\b(?:does|did|do) @ import",
                     "example": "which modules does @ import"},
                    {"pattern": r"\bimports of %s@" % _ART,
                     "example": "list the imports of the module @"},
                    {"pattern": r"\bimported by %s@" % _ART,
                     "example": "which modules are imported by @"},
                ],
                "imported-by": [  # inverse: the things that import @
                    {"pattern": r"@ (?:is|was|get|gets) imported",
                     "example": "where @ is imported"},
                    {"pattern": r"\b(?:import|imports|importing) %s@" % _ART,
                     "example": "which modules import the module @"},
                ],
            },
        },
        # The containment/definition frame-group: ONE surface frame-group,
        # TWO orientations; the container-ask orientation has TWO live
        # grammar realisations that no closed surface cue discriminates
        # (the measured S2 source: all 43 a5-nl dangerous-wrongs are
        # where-defined <-> contained-in substitutions, ZERO direction
        # flips). inventory-B refuses it; inventory-A applies the own-label
        # verb cue (contain-verbs -> contained-in, define-verbs ->
        # where-defined) and refuses only on verb conflict.
        "contain-define": {
            "relation": "part-of | code-defines",
            "keyword_gate": r"\b(?:contain|contains|contained|containing"
                            r"|hold|holds|held|inside|content|contents"
                            r"|defined|defines|define|definition)\b",
            "orientations": {
                # member-listing: entity fills the CONTAINER slot; the only
                # live realisation is contains(@) (the grammar has no
                # defines-forward op), so this orientation is unambiguous.
                "contains": [
                    {"pattern": r"\bcontents? of %s@" % _ART,
                     "example": "list the contents of the module @",
                     "verb": "contain"},
                    {"pattern": r"\b(?:does|did|do) @ (?:contain|hold)",
                     "example": "what does @ contain",
                     "verb": "contain"},
                    {"pattern": r"\b(?:does|did|do) @ define",
                     "example": "what does @ define",
                     "verb": "define"},
                    {"pattern": r"\b(?:contained|held) in %s@" % _ART,
                     "example": "what is contained in the module @",
                     "verb": "contain"},
                    {"pattern": r"\bdefined in %s@" % _ART,
                     "example": "which functions are defined in @",
                     "verb": "define"},
                    {"pattern": r"\binside %s@" % _ART,
                     "example": "what things are inside @",
                     "verb": "contain"},
                ],
                # container-ask: entity fills the MEMBER slot; live
                # realisations {contained-in(@), where-defined(@)} —
                # denotations differ by construction (list vs scalar).
                "container-ask": [
                    {"pattern": r"@ (?:is |was )?(?:contained|held) in\b"
                                r"(?! %s@)" % _ART,
                     "example": "what is @ contained in",
                     "verb": "contain"},
                    {"pattern": r"@ (?:is |was )?defined in\b(?! %s@)" % _ART,
                     "example": "which module is @ defined in",
                     "verb": "define"},
                    {"pattern": r"\b(?:contains|contain|holds|hold) %s@"
                                % _ART,
                     "example": "which module contains @",
                     "verb": "contain"},
                    {"pattern": r"\b(?:defines|define|defined) %s@" % _ART,
                     "example": "which module defines @",
                     "verb": "define"},
                    {"pattern": r"\bcontaining \w+ of %s@" % _ART,
                     "example": "what is the containing module of @",
                     "verb": "contain"},
                    # define-side passive forms below are PARITY RESTORATION
                    # (the pinned define branch was a keyword catch-all
                    # accept, so these are all inside the original
                    # acceptance set); NO contain-side analogue is added —
                    # the pinned contain cascade never accepted e.g. 'in
                    # which module is @ contained', and adding it would
                    # broaden acceptance (SS3.1 forbids).
                    {"pattern": r"\b(?:is|was|are|were) %s@ defined\b" % _ART,
                     "example": "where is @ defined",
                     "verb": "define"},
                    {"pattern": r"@ (?:is|was|get|gets) defined\b",
                     "example": "where does @ get defined",
                     "verb": "define"},
                    {"pattern": r"\bdefinition (?:\w+ )?of %s@" % _ART,
                     "example": "what module holds the definition of @",
                     "verb": "define"},
                    {"pattern": r"@ s definition\b",
                     "example": "where does @ s definition live",
                     "verb": "define"},
                ],
            },
        },
    },
    "l3a": {
        # Direction machinery (unchanged from the pinned front-end, here
        # made explicit): per-relation ROLE_DIR orientation table x the
        # role/flip surface-shape patterns of fe._l3a_shape, with
        # conflicting shape evidence already refusing (frame-ambiguous).
        "role_dir": dict(fe.ROLE_DIR),
        "shapes": {
            "role": [  # the label is applied TO the entity -> ROLE_DIR dir
                {"pattern": "LABEL of ART@", "example": "who is the R of @"},
                {"pattern": "@ s LABEL", "example": "who is @ s R"},
                {"pattern": "LABEL ART@", "example": "who Rs @  (verb form)"},
                {"pattern": "LABEL by wh", "example": "R by whom"},
                {"pattern": "does @ LABEL", "example": "does @ R anything"},
            ],
            "flip": [  # the entity FILLS the role -> flipped direction
                {"pattern": "whose LABEL is ART@",
                 "example": "whose R is @"},
                {"pattern": "@ as/for LABEL", "example": "@ as a R"},
                {"pattern": "@ is ART LABEL of",
                 "example": "who is @ the R of"},
                {"pattern": "LABEL by ART@", "example": "R by @"},
                {"pattern": "@ ... LABEL(of-final)",
                 "example": "what is @ part of"},
            ],
        },
        # NLB-0-A op-arity repair (the measured l3a S2 source: 8/8 wrongs
        # are 'Name the R of E' -> lookup instead of unique; zero direction
        # flips): imperative listing starts stop forcing lookup in role
        # shape; the head-noun's grammatical NUMBER decides, fail-closed on
        # conflict, unchanged lookup default when number is undeterminable.
        "imperative_starts": ["list ", "name ", "find "],
    },
}


def dump_inventory(path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(INVENTORY, f, indent=1, sort_keys=True)
        f.write("\n")


# =====================================================================
# a5 repaired frame layer
# =====================================================================
_KW = {g: re.compile(spec["keyword_gate"])
       for g, spec in INVENTORY["a5"].items()}
_PATS = {g: {o: [(re.compile(p["pattern"]), p.get("verb"))
              for p in pats]
             for o, pats in spec["orientations"].items()}
         for g, spec in INVENTORY["a5"].items()}


def _a5_frame_hits(t):
    """-> (keyword_groups, {(group, orientation): set(verbs)})."""
    kw_groups = [g for g, rx in sorted(_KW.items()) if rx.search(t)]
    hits = {}
    for g in kw_groups:
        for orient, pats in sorted(_PATS[g].items()):
            for rx, verb in pats:
                if rx.search(t):
                    hits.setdefault((g, orient), set()).add(verb)
    return kw_groups, hits


def a5_resolve(t, inventory_arm):
    """cleaned masked text -> {'op': ...} | refusal dict (frame layer only;
    entity/instance handling is in frame_a5 below)."""
    kw_groups, hits = _a5_frame_hits(t)
    if len(kw_groups) == 0:
        return refusal("frame-miss")
    if len(kw_groups) > 1:
        # frame-group evidence conflict (e.g. call + import keywords):
        # fail closed, never a precedence default.
        return refusal("frame-ambiguous")
    g = kw_groups[0]
    orients = sorted(set(o for (_g, o) in hits))
    if len(orients) == 0:
        return refusal("frame-miss")
    if len(orients) > 1:
        # both-orientation surface evidence: fail closed (SS3.1 rule).
        return refusal("frame-ambiguous")
    orient = orients[0]
    if g in ("call", "import"):
        return {"op": orient}
    # contain-define group
    if orient == "contains":
        return {"op": "contains"}
    # container-ask orientation: two live realisations.
    verbs = hits[(g, "container-ask")]
    if inventory_arm == "B":
        # SS3.1 fail-closed semantics: no closed surface cue discriminates
        # contained-in(@) from where-defined(@); refuse.
        return refusal("frame-ambiguous")
    # inventory-A ablation: own-label verb cue.
    if verbs == {"contain"}:
        return {"op": "contained-in"}
    if verbs == {"define"}:
        return {"op": "where-defined"}
    return refusal("frame-ambiguous")


def frame_a5(masked, ents, mapped, inventory_arm):
    concepts, abstained = mapped["concepts"], mapped["abstained"]
    if len(ents) == 0:
        return refusal("gazetteer-miss")
    if len(ents) > 1:
        return refusal("frame-ambiguous")
    ent = ents[0]
    t = fe.clean(masked)
    t = fe._LEADIN.sub("", t)
    if any(p.search(t) for p in fe._A5_INSTANCE):
        if len(concepts) == 0:
            return refusal("mapper-abstain" if abstained else "frame-miss")
        if len(concepts) > 1:
            return refusal("frame-ambiguous")
        return {"status": "parse",
                "query": {"op": "instance-of", "entity": ent,
                          "concept": concepts[0]}}
    r = a5_resolve(t, inventory_arm)
    if "status" in r:
        return r
    return {"status": "parse", "query": {"op": r["op"], "of": ent}}


# =====================================================================
# l3a repaired frame layer (op-arity repair only; direction unchanged)
# =====================================================================
def _head_noun(label_sourceid):
    words = label_sourceid.replace("-", " ").split()
    if len(words) == 1:
        return words[0]
    return words[0] if words[-1] == "of" else words[-1]


def head_number(t, label_sourceid):
    """-> 'singular' | 'plural' | 'conflict' | None from the head noun's
    matched surface form (word-boundary exact; plurals = +s/+es + closed
    irregulars). A real surface cue, not a cardinality guess."""
    w = _head_noun(label_sourceid)
    plurals = [w + "s", w + "es"] + list(fe._IRREG.get(w, ()))
    plural_hit = any(re.search(r"\b%s\b" % re.escape(p), t) for p in plurals)
    singular_hit = bool(re.search(r"\b%s\b" % re.escape(w), t))
    if plural_hit and singular_hit:
        return "conflict"
    if plural_hit:
        return "plural"
    if singular_hit:
        return "singular"
    return None


def frame_l3a(masked, ents, mapped, urn2label):
    concepts, abstained = mapped["concepts"], mapped["abstained"]
    if len(ents) == 0:
        return refusal("gazetteer-miss")
    if len(ents) > 1:
        return refusal("frame-ambiguous")
    t = fe.clean(masked)
    t = fe._LEADIN.sub("", t)
    if fe._INSTANCE_HEAD.search(t) or fe._INSTANCE_MID.search(t):
        if len(concepts) == 0:
            return refusal("mapper-abstain" if abstained else "frame-miss")
        if len(concepts) > 1:
            return refusal("frame-ambiguous")
        return {"status": "parse",
                "query": {"op": "instance", "entity": ents[0],
                          "concept": concepts[0]}}
    if len(concepts) == 0:
        return refusal("mapper-abstain" if abstained else "frame-miss")
    if len(concepts) > 1:
        return refusal("frame-ambiguous")
    rel = concepts[0]
    label = urn2label.get(rel)
    if label is None:
        return refusal("frame-miss")
    is_count = t.startswith("how many") or re.match(r"^counts? ", t)
    has_lookup_cue = (t.startswith(fe._L3A_LOOKUP_START) or
                      any(c in t for c in fe._L3A_LOOKUP_CUES))
    role_dir = fe.ROLE_DIR.get(label, "forward")
    if re.search(r"\binverse\b", t):
        direction = "inverse"
        shape = "role"
    else:
        shape = fe._l3a_shape(t, label)
        if shape == "ambiguous":
            return refusal("frame-ambiguous")
        if shape is None:
            return refusal("frame-miss")
        direction = role_dir if shape == "role" else fe._FLIP[role_dir]
    imperative = t.startswith(tuple(INVENTORY["l3a"]["imperative_starts"]))
    if is_count:
        op = "count"
    elif has_lookup_cue:
        op = "lookup"
        # NLB-0-A repair: imperative-start listing cue in role shape defers
        # to the head noun's grammatical number (fail-closed on conflict).
        if imperative and shape == "role":
            num = head_number(t, label)
            if num == "conflict":
                return refusal("frame-ambiguous")
            if num == "singular":
                op = "unique"
    elif shape == "flip":
        op = ("unique" if any(m in t for m in fe._L3A_UNIQUE_MARKERS)
              else "lookup")
    elif re.search(r"\b(?:who|whom|whose|which|what|the)\b", t):
        op = "unique"
    else:
        return refusal("frame-miss")
    return {"status": "parse",
            "query": {"op": op, "rel": rel, "direction": direction,
                      "subject": ents[0]}}


# =====================================================================
# entry point (mirrors fe.parse_all; gazetteer/mapper reused byte-identical)
# =====================================================================
def parse_all(phrasings, vertical, entity_urns, inventory_arm="B", root=None):
    root = root or _ROOT
    urn2label = fe._load_labels(root)
    gaz = fe.build_gazetteer(entity_urns)
    matcher = fe.compile_matcher(gaz)
    staged, out = [], {}
    for rec in phrasings:
        ents, masked = fe.match_entities(rec["text"], gaz, matcher)
        staged.append((rec["qid"], ents, masked))
    mapped = fe.map_batch(
        [{"pid": qid, "text": re.sub(r"\s+", " ", masked).strip()}
         for qid, _e, masked in staged],
        vertical, False)
    for qid, ents, masked in staged:
        m = mapped.get(qid, {"concepts": [], "abstained": False})
        if vertical == "l3a":
            out[qid] = frame_l3a(masked, ents, m, urn2label)
        else:
            out[qid] = frame_a5(masked, ents, m, inventory_arm)
    return out


if __name__ == "__main__":
    dump_inventory(os.path.join(_HERE, "inventory.json"))
    print("inventory written to inventory.json")
