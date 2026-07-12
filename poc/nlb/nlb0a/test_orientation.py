#!/usr/bin/env python3
"""NLB-0-A exhaustive both-orientation unit tests (design/NLB.md SS3.1/SS7.1).

Coverage is exhaustive over the INVENTORY BY CONSTRUCTION: every directional
frame x surface pattern in frontend_repaired.INVENTORY carries an 'example'
instantiation, and this suite iterates the inventory itself — a pattern added
without a passing both-orientation test fails the suite (missing example ->
error). Plus fail-closed cases: cue absence, both-orientation conflict,
cross-frame-group conflict, verb-family conflict, number conflict.

Exit 0 iff every check passes (fail-closed: any failure -> exit 1).
CPU-only, deterministic, no RNG.
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "tools", "experiments", "nlb"))
sys.path.insert(0, _HERE)

import nlb_frontend as fe  # noqa: E402
import frontend_repaired as fr  # noqa: E402

FAILURES = []
N_CHECKS = [0]


def check(name, cond, detail=""):
    N_CHECKS[0] += 1
    if not cond:
        FAILURES.append({"check": name, "detail": detail})


NO_CONCEPTS = {"concepts": [], "abstained": False}
ENT = ["urn:kotw:v0:test-entity"]


def a5(text, arm):
    return fr.frame_a5(text, ENT, NO_CONCEPTS, arm)


# =====================================================================
# a5: every group x orientation x pattern, both inventory arms
# =====================================================================
def test_a5_inventory():
    expected_b = {  # inventory-B resolution per (group, orientation)
        ("call", "callees-of"): "callees-of",
        ("call", "callers-of"): "callers-of",
        ("import", "imports-of"): "imports-of",
        ("import", "imported-by"): "imported-by",
        ("contain-define", "contains"): "contains",
        ("contain-define", "container-ask"): "REFUSE:frame-ambiguous",
    }
    for group, spec in sorted(fr.INVENTORY["a5"].items()):
        for orient, pats in sorted(spec["orientations"].items()):
            for p in pats:
                check("a5-example-present:%s/%s" % (group, orient),
                      "example" in p and "@" in p["example"],
                      p.get("pattern"))
                text = p["example"]
                # the example must actually exercise ITS OWN pattern
                check("a5-example-matches-own-pattern:%s" % p["pattern"],
                      re.search(p["pattern"], fe.clean(text)) is not None,
                      text)
                want = expected_b[(group, orient)]
                got = a5(text, "B")
                if want.startswith("REFUSE:"):
                    check("a5-B:%s/%s:%s" % (group, orient, text),
                          got["status"] == "refuse" and
                          got["stage"] == want.split(":")[1],
                          json.dumps(got))
                else:
                    check("a5-B:%s/%s:%s" % (group, orient, text),
                          got["status"] == "parse" and
                          got["query"]["op"] == want and
                          got["query"]["of"] == ENT[0],
                          json.dumps(got))
                # inventory-A: identical except container-ask resolves by
                # own-label verb
                got_a = a5(text, "A")
                if (group, orient) == ("contain-define", "container-ask"):
                    want_a = ("contained-in" if p["verb"] == "contain"
                              else "where-defined")
                    check("a5-A:%s:%s" % (orient, text),
                          got_a["status"] == "parse" and
                          got_a["query"]["op"] == want_a,
                          json.dumps(got_a))
                else:
                    check("a5-A-same-as-B:%s:%s" % (orient, text),
                          json.dumps(got_a, sort_keys=True) ==
                          json.dumps(got, sort_keys=True),
                          json.dumps(got_a))


def test_a5_fail_closed():
    cases = [
        # both orientations of one group -> refuse (both arms)
        ("which routines call @ and which routines does @ call",
         "frame-ambiguous"),
        ("which modules import @ and what does @ import",
         "frame-ambiguous"),
        ("which module contains @ and what does @ contain",
         "frame-ambiguous"),
        # cross-frame-group keyword evidence -> refuse (no precedence)
        ("which module imports and calls @", "frame-ambiguous"),
        ("does @ call or contain anything", "frame-ambiguous"),
        # cue absence -> frame-miss
        ("tell me about @", "frame-miss"),
        ("what is the purpose of @", "frame-miss"),
    ]
    for text, stage in cases:
        for arm in ("A", "B"):
            got = a5(text, arm)
            check("a5-failclosed[%s]:%s" % (arm, text),
                  got["status"] == "refuse" and got["stage"] == stage,
                  json.dumps(got))
    # verb-family conflict in container-ask: refuse under BOTH arms
    for text in ("which module holds @ and defines @",
                 "where is @ defined and what holds @"):
        for arm in ("A", "B"):
            got = a5(text, arm)
            check("a5-verbconflict[%s]:%s" % (arm, text),
                  got["status"] == "refuse", json.dumps(got))
    # single-adjacent-verb crossing: inventory-A follows its own-label cue
    # (the pinned convention — this is exactly the class it leaves alive);
    # inventory-B refuses it
    got = a5("which module contains and defines @", "A")
    check("a5-A-own-label-crossing",
          got["status"] == "parse" and
          got["query"]["op"] == "where-defined", json.dumps(got))
    got = a5("which module contains and defines @", "B")
    check("a5-B-own-label-crossing-refused",
          got["status"] == "refuse" and
          got["stage"] == "frame-ambiguous", json.dumps(got))
    # member-orientation with both verb families: uniquely realisable ->
    # contains (the repaired reading of the measured 'contain or define'
    # dangerous-wrong item)
    for arm in ("A", "B"):
        got = a5("what does @ contain or define", arm)
        check("a5-member-contain-or-define[%s]" % arm,
              got["status"] == "parse" and got["query"]["op"] == "contains",
              json.dumps(got))
    # multi-entity and zero-entity guards
    got = fr.frame_a5("does @ call @", ["u1", "u2"], NO_CONCEPTS, "B")
    check("a5-two-entities", got["status"] == "refuse" and
          got["stage"] == "frame-ambiguous", json.dumps(got))
    got = fr.frame_a5("does x call y", [], NO_CONCEPTS, "B")
    check("a5-zero-entities", got["status"] == "refuse" and
          got["stage"] == "gazetteer-miss", json.dumps(got))


# =====================================================================
# l3a: both orientations for EVERY ROLE_DIR relation x shape pattern
# =====================================================================
def _label_urns(root):
    urn2label = fe._load_labels(root)
    out = {}
    for urn, label in urn2label.items():
        if label in fr.INVENTORY["l3a"]["role_dir"] and label not in out:
            out[label] = urn
    return out, urn2label


def _role_instantiations(label):
    """Surface instantiations exercising each ROLE-shape pattern of
    fe._l3a_shape for this label (mechanical; nonsense English is fine —
    the pattern mechanics are under test)."""
    return [
        ("who is the %s of @" % label.replace("-", " "), "p1:L-of-ART@"),
        ("who is @ s %s" % label.replace("-", " "), "p2:@-s-L"),
        ("who is %s the @" % label.replace("-", " "), "p3:L-ART@"),
        ("%s by whom" % label.replace("-", " "), "p4:L-by-wh"),
        ("does @ %s" % label.replace("-", " "), "p5:does-@-L"),
    ]


def _flip_instantiations(label):
    l = label.replace("-", " ")
    out = [
        ("whose %s is @" % l, "f1:whose-L-is-@"),
        ("@ as a %s" % l, "f2:@-as-L"),
        ("who is @ the %s of" % l, "f3:@-is-L-of"),
        ("%s by @" % l, "f4:L-by-@"),
    ]
    if label.split("-")[-1] == "of":
        out.append(("what is @ %s" % l, "f5:of-final-bare"))
    return out


def test_l3a_shape_inventory():
    role_dir = fr.INVENTORY["l3a"]["role_dir"]
    check("l3a-inventory-matches-pinned-ROLE_DIR",
          role_dir == fe.ROLE_DIR, json.dumps(role_dir))
    for label, rdir in sorted(role_dir.items()):
        of_final = label.split("-")[-1] == "of"
        for text, pid in _role_instantiations(label):
            got = fe._l3a_shape(fe.clean(text), label)
            if of_final and pid.startswith("p5"):
                # of-final labels: 'does @ ... L' inherently co-matches the
                # of-final flip pattern -> fail-closed 'ambiguous' is the
                # CORRECT outcome (conflicting orientation evidence)
                check("l3a-role-offinal-conflict:%s:%s" % (label, pid),
                      got == "ambiguous", "%r -> %r" % (text, got))
                continue
            check("l3a-role:%s:%s" % (label, pid), got == "role",
                  "%r -> %r" % (text, got))
        for text, pid in _flip_instantiations(label):
            got = fe._l3a_shape(fe.clean(text), label)
            check("l3a-flip:%s:%s" % (label, pid), got == "flip",
                  "%r -> %r" % (text, got))
        # direction mapping: role -> ROLE_DIR, flip -> flipped
        check("l3a-dir-map:%s" % label,
              fe._FLIP[rdir] != rdir and fe._FLIP[fe._FLIP[rdir]] == rdir,
              rdir)
        # both-orientation conflict -> ambiguous (fail-closed)
        conflict = "whose %s is @ s %s" % (label.replace("-", " "),
                                           label.replace("-", " "))
        got = fe._l3a_shape(fe.clean(conflict), label)
        check("l3a-conflict:%s" % label, got == "ambiguous",
              "%r -> %r" % (conflict, got))
        # cue absence -> None (fail-closed frame-miss upstream)
        got = fe._l3a_shape("tell me about @", label)
        check("l3a-absent:%s" % label, got is None, repr(got))


def test_l3a_imperative_number_repair():
    labels, urn2label = _label_urns(_ROOT)
    mother = labels["mother"]
    mapped = {"concepts": [mother], "abstained": False}

    def run(text):
        return fr.frame_l3a(text, ENT, mapped, urn2label)

    # singular definite head -> unique (the measured 8/8 wrong class)
    for text in ("name the mother of @", "name @ s mother",
                 "find the mother of @", "list the mother of @"):
        got = run(text)
        check("l3a-imperative-singular:%s" % text,
              got["status"] == "parse" and got["query"]["op"] == "unique"
              and got["query"]["direction"] == "forward",
              json.dumps(got))
    # plural head -> lookup (unchanged listing semantics)
    for text in ("name the mothers of @", "list the mothers of @"):
        got = run(text)
        check("l3a-imperative-plural:%s" % text,
              got["status"] == "parse" and got["query"]["op"] == "lookup",
              json.dumps(got))
    # number conflict -> fail-closed refusal
    got = run("name the mother and mothers of @")
    check("l3a-imperative-number-conflict",
          got["status"] == "refuse" and got["stage"] == "frame-ambiguous",
          json.dumps(got))
    # non-imperative behaviour unchanged: wh-singular -> unique
    got = run("who is the mother of @")
    check("l3a-wh-unique", got["status"] == "parse" and
          got["query"]["op"] == "unique", json.dumps(got))
    # flip shape keeps the non-guessing lookup default under imperatives
    got = run("name everyone whose mother is @")
    check("l3a-flip-imperative-lookup", got["status"] == "parse" and
          got["query"]["op"] == "lookup" and
          got["query"]["direction"] == "inverse", json.dumps(got))
    # count cue precedence unchanged
    got = run("how many children does @ have as mother")
    check("l3a-count-unchanged",
          got["status"] != "parse" or got["query"]["op"] == "count",
          json.dumps(got))


def main():
    test_a5_inventory()
    test_a5_fail_closed()
    test_l3a_shape_inventory()
    test_l3a_imperative_number_repair()
    report = {"schema": "nlb0a-orientation-tests/1",
              "n_checks": N_CHECKS[0],
              "n_failures": len(FAILURES),
              "failures": FAILURES,
              "green": not FAILURES}
    os.makedirs(os.path.join(_HERE, "results"), exist_ok=True)
    with open(os.path.join(_HERE, "results", "orientation-tests.json"),
              "w") as f:
        json.dump(report, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: report[k] for k in
                      ("n_checks", "n_failures", "green")}, indent=1))
    if FAILURES:
        print(json.dumps(FAILURES[:20], indent=1))
    sys.exit(0 if report["green"] else 1)


if __name__ == "__main__":
    main()
