#!/usr/bin/env python3
"""nlb_frontend — deterministic NL -> closed-grammar front-end (v1, DEV-final).

The pipeline under test for l3a-parse / a5-nl
(docs/design-nl-boundary-l3a-parse-a5-nl.md section 3):

  [1] entity gazetteer  (longest-match over surface text; built from the
                         pinned world stores' entity URN slugs)
  [2] mapper a1-hybrid  (via tools/experiments/nlb/nlb_map.mjs — the real
                         kernel-mapper build, policy pin verified there)
  [3] closed frame layer (the rule sets below)

FRAME RULES v1: finalised against the DEV phrasing sets ONLY
(data/nlb-phrasings-*/dev.jsonl, design doc section 5.3). After this file's
sha256 is pinned in the records, ANY edit mints a new record id. The rules are
a CLOSED, deterministic system over the closed grammar + the pinned lexicon
labels; they contain:
  - a per-relation surface-orientation table (ROLE_DIR): which engine
    direction realises the role reading "the R of E" for each relation with
    world edges (design doc section 3 — closed grammar-like knowledge, NOT
    answer knowledge);
  - a label-variant matcher (plural/verb inflections of the mapped concept's
    OWN label + the two irregulars 'made'->make, 'children'->child). It NEVER
    maps synonyms: concept binding belongs to the mapper alone (no alias
    layer — design doc section 3; a lexicon miss must stay a mapper miss so
    stage indictment and the G5 derangement stay clean).

Fail-closed contract: every non-parse is {"status":"refuse","code":"ERR_PARSE",
"stage":<gazetteer-miss|mapper-abstain|frame-miss|frame-ambiguous>}. The
front-end NEVER guesses a slot; conflicting direction evidence refuses; the
op default in inverse-possessive shape is lookup (the non-guessing op — a
cardinality guess of 'unique' could fabricate a scalar answer). No RNG
anywhere; the deranged arm's permutations are the registered seed-0 rotations
(concept URNs in nlb_map.mjs; relational ops below for the a5 vertical).
"""

import json
import os
import re
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_ENT_PREFIX = "urn:kotw:v0:"

A5_OPS = sorted(["callees-of", "callers-of", "contained-in", "contains",
                 "imported-by", "imports-of", "where-defined"])
# Registered seed-0 derangement of the a5 relational-op bindings (rotation).
A5_OP_DERANGE = {op: A5_OPS[(i + 1) % len(A5_OPS)] for i, op in enumerate(A5_OPS)}

# Role reading "the R of E" / "E's R": which engine direction it realises,
# per relation label (sourceId). Only relations with world edges need a
# non-default entry: a wrong default on an edgeless relation is refused by
# the engine (ERR_TERM_UNLICENSED), never answered.
ROLE_DIR = {"mother": "forward", "father": "forward",
            "maker-of": "inverse", "part-of": "inverse", "has-part": "forward"}
_FLIP = {"forward": "inverse", "inverse": "forward"}

# Closed irregular-form table for label-variant matching (frame-side ONLY;
# the mapper has its own lemmatizer). Deliberately tiny.
_IRREG = {"make": ("made",), "child": ("children",)}


def refusal(stage):
    return {"status": "refuse", "code": "ERR_PARSE", "stage": stage}


# ---------------------------------------------------------------- lexicon labels
_URN2LABEL = {}


def _load_labels(root):
    key = root
    if key in _URN2LABEL:
        return _URN2LABEL[key]
    m = {}
    for corpus in ("kernel-v0", "molecules-v0", "code-v0"):
        p = os.path.join(root, "data", corpus, "minted-urns.jsonl")
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    m[r["urn"]] = r["sourceId"]
    _URN2LABEL[key] = m
    return m


def _word_variants(w):
    out = [w, w + "s", w + "es", w + "d", w + "ed", w + "r", w + "er",
           w + "rs", w + "ers", w + "ing"]
    out.extend(_IRREG.get(w, ()))
    return out


def _label_alt(label_sourceid):
    """Regex alternation matching inflected occurrences of the label's OWN
    surface form (head-word variants; tail words literal)."""
    words = label_sourceid.replace("-", " ").split()
    head = "(?:%s)" % "|".join(sorted(_word_variants(words[0]), key=len,
                                      reverse=True))
    if len(words) == 1:
        return head
    return head + "".join(" " + re.escape(w) for w in words[1:])


# ---------------------------------------------------------------- gazetteer
def build_gazetteer(entity_urns):
    """surface string -> entity URN; ambiguous surfaces are DROPPED (a later
    match on them is a gazetteer-miss -> ERR_PARSE, never a guess)."""
    gaz = {}
    ambiguous = set()
    for urn in entity_urns:
        if not urn.startswith(_ENT_PREFIX):
            continue
        slug = urn[len(_ENT_PREFIX):].lower()
        for surface in {slug, slug.replace("-", " ")}:
            surface = surface.strip()
            if not surface:
                continue
            if surface in gaz and gaz[surface] != urn:
                ambiguous.add(surface)
            else:
                gaz[surface] = urn
    for s in ambiguous:
        gaz.pop(s, None)
    return gaz


def compile_matcher(gaz):
    """One combined alternation regex, alternatives sorted longest-first, so a
    single left-to-right scan realises longest-match-first non-overlapping
    matching deterministically (compiled ONCE per parse_all call)."""
    ordered = sorted(gaz, key=lambda s: (-len(s), s))
    if not ordered:
        return None
    return re.compile(r"(?<![a-z0-9_])(?:" +
                      "|".join(re.escape(s) for s in ordered) +
                      r")(?![a-z0-9_])")


def match_entities(text, gaz, matcher):
    """Longest-match-first, non-overlapping; returns ([urn...], masked_text)."""
    low = text.lower()
    taken = []  # (start, end, urn)
    if matcher is not None:
        for m in matcher.finditer(low):
            taken.append((m.start(), m.end(), gaz[m.group(0)]))
    out, prev, ents = [], 0, []
    for s, e, urn in taken:
        out.append(low[prev:s])
        out.append(" @ ")
        ents.append(urn)
        prev = e
    out.append(low[prev:])
    return ents, "".join(out)


def clean(masked):
    """Deterministic normalisation of the masked text before frame matching:
    lowercase (already), unicode dash/apostrophe folding, possessive
    's -> ' s ', punctuation stripped to spaces, whitespace collapsed."""
    t = masked
    t = t.replace("—", " ").replace("–", " ").replace("’", "'")
    t = re.sub(r"'s\b", " s", t)
    t = t.replace("'", " ")
    t = re.sub(r"[?!.,;:\"()\[\]]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------- mapper step
def map_batch(masked_records, vertical, derange):
    """masked_records: [{pid, text}]; returns {pid: {concepts, abstained}}."""
    cmd = ["node", os.path.join(_HERE, "nlb_map.mjs"), "--vertical", vertical]
    if derange:
        cmd.append("--derange")
    payload = "\n".join(json.dumps(r, sort_keys=True) for r in masked_records)
    proc = subprocess.run(cmd, input=payload, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("nlb_map.mjs failed: %s" % proc.stderr[:2000])
    out = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["pid"]] = r
    return out


# ---------------------------------------------------------------- l3a frame
_LEADIN = re.compile(r"^(?:please |can you |could you |would you |tell me "
                     r"|say |show me |give me )+")
_L3A_LOOKUP_START = ("list ", "name ", "find ")
_L3A_LOOKUP_CUES = ("who are", "what are", "which people", "which items",
                    "which things", "which men", "which women", "what things",
                    "what items", "what people", "everyone", "everything",
                    "all the")
_L3A_UNIQUE_MARKERS = ("the one ", "exactly one", "the unique ", "the single ",
                       "one single ")
_INSTANCE_HEAD = re.compile(r"^(?:is|was) (?:the |a |an )?@ (?:a|an|one of) ")
_INSTANCE_MID = re.compile(r"@ (?:is|was) (?:a|an) ")


def _l3a_shape(t, label_sourceid):
    """-> 'role' | 'flip' | 'ambiguous' | None on the cleaned masked text.
    role = the label is applied TO the entity ('the R of @', '@ s R',
    'R-verb @', 'R by wh'); flip = the entity FILLS the role for someone else
    ('whose R is @', '@ as R', '@ the R of', '@ part of', 'R by @')."""
    alt = _label_alt(label_sourceid)
    art = r"(?:the |a |an )?"
    role = [r"\b%s of %s@" % (alt, art),
            r"@ s %s\b" % alt,
            r"\b%s %s@" % (alt, art),
            r"\b%s by (?:whom|who)\b" % alt,
            r"\b(?:does|did|do) @ (?:\w+ )?%s\b" % alt]
    flip = [r"whose %s (?:is|was) %s@" % (alt, art),
            r"@ (?:as|for) (?:a |an |the |their |its )?%s\b" % alt,
            r"@ (?:is |was )?%s%s of\b(?! %s@)" % (art, alt, art),
            r"\b%s by %s@" % (alt, art)]
    words = label_sourceid.replace("-", " ").split()
    if words[-1] == "of":
        # of-final labels ('maker of', 'part of'): the bare '@ ... R' form is
        # the entity-first reading ('what is @ part of')
        flip.append(r"@ (?:is |was )?(?:a |the )?%s\b(?! %s@)" % (alt, art))
    r_hit = any(re.search(p, t) for p in role)
    f_hit = any(re.search(p, t) for p in flip)
    if r_hit and f_hit:
        # one construction can legitimately satisfy both pattern families only
        # via overlapping spans; treat as conflicting evidence -> refuse
        return "ambiguous"
    if r_hit:
        return "role"
    if f_hit:
        return "flip"
    return None


def _frame_l3a(masked, ents, mapped, urn2label):
    concepts, abstained = mapped["concepts"], mapped["abstained"]
    if len(ents) == 0:
        return refusal("gazetteer-miss")
    if len(ents) > 1:
        return refusal("frame-ambiguous")
    t = clean(masked)
    t = _LEADIN.sub("", t)
    # instance shape first (concept slot, no direction)
    if _INSTANCE_HEAD.search(t) or _INSTANCE_MID.search(t):
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
    # op cue (count > lookup-cue > shape default)
    is_count = t.startswith("how many") or re.match(r"^counts? ", t)
    has_lookup_cue = (t.startswith(_L3A_LOOKUP_START) or
                      any(c in t for c in _L3A_LOOKUP_CUES))
    # direction from shape
    if label is None:
        return refusal("frame-miss")
    role_dir = ROLE_DIR.get(label, "forward")
    if re.search(r"\binverse\b", t):
        direction = "inverse"  # explicit grammar keyword (scaffold path)
        shape = "role"
    else:
        shape = _l3a_shape(t, label)
        if shape == "ambiguous":
            return refusal("frame-ambiguous")
        if shape is None:
            return refusal("frame-miss")
        direction = role_dir if shape == "role" else _FLIP[role_dir]
    if is_count:
        op = "count"
    elif has_lookup_cue:
        op = "lookup"
    elif shape == "flip":
        # inverse-possessive default: lookup (set-valued, non-guessing) unless
        # the phrasing carries an explicit exactly-one marker
        op = "unique" if any(m in t for m in _L3A_UNIQUE_MARKERS) else "lookup"
    elif re.search(r"\b(?:who|whom|whose|which|what|the)\b", t):
        op = "unique"
    else:
        return refusal("frame-miss")
    return {"status": "parse",
            "query": {"op": op, "rel": rel, "direction": direction,
                      "subject": ents[0]}}


# ---------------------------------------------------------------- a5 frame
_A5_INSTANCE = (re.compile(r"^(?:is|was) (?:the )?@ (?:a|an) "),
                re.compile(r"@ (?:is|was) (?:a|an) "),
                re.compile(r"\bclass @ as (?:a|an) "),
                re.compile(r"\bwhether @ (?:is|was) (?:a|an) "))

_A5_DEFINE = re.compile(r"\b(?:defined|defines|define|definition)\b")
_A5_CALL = re.compile(r"\b(?:call|calls|called|calling|caller|callers|callee"
                      r"|callees|invoke|invokes|invoked|invoking)\b")
_A5_IMPORT = re.compile(r"\b(?:import|imports|imported|importing)\b")
_A5_CONTAIN = re.compile(r"\b(?:contain|contains|contained|containing|hold"
                         r"|holds|held|inside|content|contents)\b")
# article + one optional closed-class kind-noun before the entity slot
# ("contains the function @", "calls the routine @") — closed list, no \w+
_ART = (r"(?:the |a |an )?(?:function |functions |module |modules |class "
        r"|classes |method |methods |routine |routines |file |files )?")


def _a5_op(t):
    """Ordered, first-match keyword cascade (finalised on DEV only)."""
    if _A5_DEFINE.search(t):
        return "where-defined"
    if _A5_CALL.search(t):
        for pat, op in (
                (r"\bcalls (?:does|did) @", "callees-of"),
                (r"\b(?:does|did|do) @ (?:call|invoke)", "callees-of"),
                (r"\bcallees of %s@" % _ART, "callees-of"),
                (r"\bcallers of %s@" % _ART, "callers-of"),
                (r"\b(?:called|invoked) (?:by|from) %s@" % _ART, "callees-of"),
                (r"@ (?:is|was|get|gets) (?:called|invoked)", "callers-of"),
                (r"\bcalls to %s@" % _ART, "callers-of"),
                (r"\b(?:call|calls|invoke|invokes|calling|invoking) %s@"
                 % _ART, "callers-of")):
            if re.search(pat, t):
                return op
        return None
    if _A5_IMPORT.search(t):
        for pat, op in (
                (r"\b(?:does|did|do) @ import", "imports-of"),
                (r"\bimports of %s@" % _ART, "imports-of"),
                (r"\bimported by %s@" % _ART, "imports-of"),
                (r"@ (?:is|was|get|gets) imported", "imported-by"),
                (r"\b(?:import|imports|importing) %s@" % _ART, "imported-by")):
            if re.search(pat, t):
                return op
        return None
    if _A5_CONTAIN.search(t):
        for pat, op in (
                (r"\bcontents? of %s@" % _ART, "contains"),
                (r"\b(?:does|did|do) @ (?:contain|hold)", "contains"),
                (r"@ (?:is |was )?(?:contained|held) in\b(?! %s@)" % _ART,
                 "contained-in"),
                (r"\b(?:contained|held) in %s@" % _ART, "contains"),
                (r"\binside %s@" % _ART, "contains"),
                (r"\bcontaining \w+ of %s@" % _ART, "contained-in"),
                (r"\b(?:contains|contain|holds|hold) %s@" % _ART,
                 "contained-in")):
            if re.search(pat, t):
                return op
        return None
    return None


def _frame_a5(masked, ents, mapped, derange):
    concepts, abstained = mapped["concepts"], mapped["abstained"]
    if len(ents) == 0:
        return refusal("gazetteer-miss")
    if len(ents) > 1:
        return refusal("frame-ambiguous")
    ent = ents[0]
    t = clean(masked)
    t = _LEADIN.sub("", t)
    if any(p.search(t) for p in _A5_INSTANCE):
        if len(concepts) == 0:
            return refusal("mapper-abstain" if abstained else "frame-miss")
        if len(concepts) > 1:
            return refusal("frame-ambiguous")
        return {"status": "parse",
                "query": {"op": "instance-of", "entity": ent,
                          "concept": concepts[0]}}
    op = _a5_op(t)
    if op is None:
        return refusal("frame-miss")
    if derange:
        op = A5_OP_DERANGE[op]
    return {"status": "parse", "query": {"op": op, "of": ent}}


# ---------------------------------------------------------------- entry point
def parse_all(phrasings, vertical, entity_urns, derange=False, root=None):
    """phrasings: [{qid, text}] -> {qid: parse-or-refusal dict}."""
    root = root or _ROOT
    urn2label = _load_labels(root)
    gaz = build_gazetteer(entity_urns)
    matcher = compile_matcher(gaz)
    staged, out = [], {}
    for rec in phrasings:
        ents, masked = match_entities(rec["text"], gaz, matcher)
        staged.append((rec["qid"], ents, masked))
    mapped = map_batch(
        [{"pid": qid, "text": re.sub(r"\s+", " ", masked).strip()}
         for qid, _e, masked in staged],
        vertical, derange)
    for qid, ents, masked in staged:
        m = mapped.get(qid, {"concepts": [], "abstained": False})
        if vertical == "l3a":
            out[qid] = _frame_l3a(masked, ents, m, urn2label)
        else:
            out[qid] = _frame_a5(masked, ents, m, derange)
    return out
