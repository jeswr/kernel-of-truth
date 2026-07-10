#!/usr/bin/env python3
"""nlb_frontend — deterministic NL -> closed-grammar front-end (DRAFT v0).

The pipeline under test for l3a-parse / a5-nl
(docs/design-nl-boundary-l3a-parse-a5-nl.md section 3):

  [1] entity gazetteer  (longest-match over surface text; built from the
                         pinned world stores' entity URN slugs)
  [2] mapper a1-hybrid  (via tools/experiments/nlb/nlb_map.mjs — the real
                         @jeswr/kernel-mapper build, policy pin verified there)
  [3] closed frame layer (the rule sets below)

FRAME RULES ARE DRAFT: per the blindness protocol (design doc section 5.3)
they may be revised against the blind DEV phrasing set ONLY, then this file's
sha256 is pinned in the records BEFORE the held-out eval phrasings are
authored. Any later edit mints a new record id.

Fail-closed contract: every non-parse is {"status":"refuse","code":"ERR_PARSE",
"stage":<gazetteer-miss|mapper-abstain|frame-miss|frame-ambiguous>}. The
front-end NEVER guesses a slot. No RNG anywhere; the deranged arm's
permutations are the registered seed-0 rotations (concept URNs in nlb_map.mjs;
relational ops below for the a5 vertical, whose op keywords carry the
relational semantics — record a5-nl, arms_mandatory_baselines).
"""

import json
import os
import re
import subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_ENT_PREFIX = "urn:kotw:v0:"

A5_OPS = sorted(["callees-of", "callers-of", "contained-in", "contains",
                 "imported-by", "imports-of", "where-defined"])
# Registered seed-0 derangement of the a5 relational-op bindings (rotation).
A5_OP_DERANGE = {op: A5_OPS[(i + 1) % len(A5_OPS)] for i, op in enumerate(A5_OPS)}


def refusal(stage):
    return {"status": "refuse", "code": "ERR_PARSE", "stage": stage}


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


def match_entities(text, gaz, ordered_surfaces):
    """Longest-match-first, non-overlapping; returns ([urn...], masked_text)."""
    low = text.lower()
    taken = []  # (start, end, urn)

    def overlaps(a, b):
        return not (a[1] <= b[0] or b[1] <= a[0])

    for surface in ordered_surfaces:
        pat = re.compile(r"(?<![a-z0-9_])" + re.escape(surface) + r"(?![a-z0-9_])")
        for m in pat.finditer(low):
            span = (m.start(), m.end(), gaz[surface])
            if not any(overlaps(span, t) for t in taken):
                taken.append(span)
    taken.sort()
    out, prev, ents = [], 0, []
    for s, e, urn in taken:
        out.append(low[prev:s])
        out.append(" @ ")
        ents.append(urn)
        prev = e
    out.append(low[prev:])
    masked = re.sub(r"\s+", " ", "".join(out)).strip()
    return ents, masked


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


# ---------------------------------------------------------------- frame layer
def _frame_l3a(masked, ents, mapped):
    t = " %s " % masked
    concepts, abstained = mapped["concepts"], mapped["abstained"]
    direction = "inverse" if " inverse " in t else "forward"
    if masked.startswith("how many"):
        op = "count"
    elif masked.startswith("list"):
        op = "lookup"
    elif masked.startswith(("who is", "who was", "what is")):
        op = "unique"
    elif masked.startswith("is ") and (" a " in t or " an " in t):
        op = "instance"
    else:
        return refusal("frame-miss")
    if len(ents) == 0:
        return refusal("gazetteer-miss")
    if len(ents) > 1:
        return refusal("frame-ambiguous")
    if len(concepts) == 0:
        return refusal("mapper-abstain" if abstained else "frame-miss")
    if len(concepts) > 1:
        return refusal("frame-ambiguous")
    if op == "instance":
        return {"status": "parse",
                "query": {"op": "instance", "entity": ents[0], "concept": concepts[0]}}
    return {"status": "parse",
            "query": {"op": op, "rel": concepts[0], "direction": direction,
                      "subject": ents[0]}}


def _frame_a5(masked, ents, mapped, derange):
    t = " %s " % masked
    concepts, abstained = mapped["concepts"], mapped["abstained"]
    if len(ents) == 0:
        return refusal("gazetteer-miss")
    if len(ents) > 1:
        return refusal("frame-ambiguous")
    ent = ents[0]
    if masked.startswith("is ") and (" a " in t or " an " in t):
        if len(concepts) == 0:
            return refusal("mapper-abstain" if abstained else "frame-miss")
        if len(concepts) > 1:
            return refusal("frame-ambiguous")
        return {"status": "parse",
                "query": {"op": "instance-of", "entity": ent, "concept": concepts[0]}}
    if "does @ call" in t:
        op = "callees-of"
    elif "call" in t:
        op = "callers-of"
    elif "does @ import" in t:
        op = "imports-of"
    elif "import" in t:
        op = "imported-by"
    elif "does @ contain" in t:
        op = "contains"
    elif "contain" in t:
        op = "contained-in"
    elif "defined" in t:
        op = "where-defined"
    else:
        return refusal("frame-miss")
    if derange:
        op = A5_OP_DERANGE[op]
    return {"status": "parse", "query": {"op": op, "of": ent}}


# ---------------------------------------------------------------- entry point
def parse_all(phrasings, vertical, entity_urns, derange=False):
    """phrasings: [{qid, text}] -> {qid: parse-or-refusal dict}."""
    gaz = build_gazetteer(entity_urns)
    ordered = sorted(gaz, key=lambda s: (-len(s), s))
    staged, out = [], {}
    for rec in phrasings:
        ents, masked = match_entities(rec["text"], gaz, ordered)
        staged.append((rec["qid"], ents, masked))
    mapped = map_batch(
        [{"pid": qid, "text": masked} for qid, _e, masked in staged],
        vertical, derange)
    for qid, ents, masked in staged:
        m = mapped.get(qid, {"concepts": [], "abstained": False})
        if vertical == "l3a":
            out[qid] = _frame_l3a(masked, ents, m)
        else:
            out[qid] = _frame_a5(masked, ents, m, derange)
    return out
