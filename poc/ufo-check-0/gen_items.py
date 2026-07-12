#!/usr/bin/env python3
"""UFO-CHECK-0 item generator (design §2; PROPOSED-ASM-1480).

Writes data/ufo-sn3-items-v0/{items.jsonl, meta.json}. Deterministic from the
registered seed string 'ufo-check-0/1|two-situation-modal-rigidity|20260712'
(explicit seed per repo convention; the encoder itself remains seedless —
CLAUDE.md). Rerunning byte-reproduces the corpus.

Composition (design §2): 4 families x 150 scored = 600 scored items, every
one a member of a near-miss pair (75 pairs per family; base and companion
differ by exactly ONE load-bearing fact and their golds differ), balanced
50 E / 50 C / 50 U per family; + 30 OUT-OF-PROFILE probes (excluded from the
scored slice). Gold NEVER appears in the corpus — it is engine-derived by
materialise.py (PROPOSED-ASM-1481).

Prompt surface (identical bytes across ALL arms; canonical deterministic
templates, one fact per line, FIXED order — design §2 + skeptic item 6).
"""

import argparse
import hashlib
import json
import os

SEED_STRING = "ufo-check-0/1|two-situation-modal-rigidity|20260712"

# Global type-name pools with GLOBALLY CONSISTENT meta assignment (a name is
# the same meta-kind in every item), so the AD arm's global Sattolo
# derangement of the name->meta assignment is well-defined (design §5).
KINDS = ["Person", "Rock", "Cat", "Tree", "Robot", "Fish", "Building",
         "Star", "Book", "River"]
SUBKINDS = ["Novel", "Sculptor", "Kitten", "Oak", "Drone", "Trout"]
SUBKIND_PARENT = {"Novel": "Book", "Sculptor": "Person", "Kitten": "Cat",
                  "Oak": "Tree", "Drone": "Robot", "Trout": "Fish"}
ROLES = ["Student", "Employee", "Tenant", "Customer", "Voter", "Pilot",
         "Juror", "Donor"]
PHASES = ["Child", "Adult", "Seedling", "Larva", "Puppy", "Elder"]
META = {}
META.update({k: "kind" for k in KINDS})
META.update({k: "subkind" for k in SUBKINDS})
META.update({k: "role" for k in ROLES})
META.update({k: "phase" for k in PHASES})
ENTITIES = ["bo", "ann", "rex", "kim", "ida", "ute", "max", "joy", "sam",
            "lee"]


def rng_int(*keys):
    h = hashlib.sha256(("\x1f".join([SEED_STRING] + [str(k) for k in keys])
                        ).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


def pick(pool, *keys):
    return pool[rng_int(*keys) % len(pool)]


def pick2(pool, *keys):
    a = pick(pool, *keys, "a")
    b = pool[(pool.index(a) + 1 + rng_int(*keys, "b") % (len(pool) - 1))
             % len(pool)]
    return a, b


# ---------------------------------------------------------------- prompt --
def verbalise(facts, candidate_text):
    lines = ["Situations: %s." % ", ".join(sorted(facts["situations"]))]
    for a, b in sorted(facts.get("accessible", [])):
        lines.append("Situation %s is possible from situation %s." % (b, a))
    for t in sorted(facts["meta_types"]):
        lines.append("'%s' is a %s type." % (t, facts["meta_types"][t]))
    for sub, sup in sorted(facts.get("subsumptions", [])):
        lines.append("'%s' specialises '%s'." % (sub, sup))
    for x, s in sorted(facts.get("exists", [])):
        lines.append("'%s' exists in situation %s." % (x, s))
    for s, x, t in sorted(facts.get("holds", [])):
        lines.append("In %s, '%s' is a '%s'." % (s, x, t))
    for s, x, t in sorted(facts.get("not_holds", [])):
        lines.append("In %s, '%s' is not a '%s'." % (s, x, t))
    for s, t in sorted(facts.get("closed_for", [])):
        lines.append("The recorded '%s' membership facts for situation %s "
                     "are complete." % (t, s))
    lines.append("Candidate claim: %s" % candidate_text)
    lines.append("Answer with exactly one word: ENTAILED, CONTRADICTED, or "
                 "UNDERDETERMINED.")
    return "\n".join(lines)


def cand_membership(s, e, t):
    return ({"form": "membership", "situation": s, "entity": e, "type": t},
            "In %s, '%s' is a '%s'." % (s, e, t))


def cand_necessity(e, t):
    return ({"form": "necessity", "entity": e, "type": t},
            "'%s' is a '%s' in every declared situation." % (e, t))


def cand_spec(s, sub, sup):
    return ({"form": "spec_consequence", "situation": s, "sub": sub,
             "super": sup},
            "Every '%s' in %s is thereby a '%s' in %s (via the stated "
            "specialisation)." % (sub, s, sup, s))


def base_facts(e, extra_types=()):
    return {"situations": ["S1", "S2"], "accessible": [["S1", "S2"]],
            "meta_types": {}, "subsumptions": [], "exists": [],
            "holds": [], "not_holds": [], "closed_for": []}


def add_distractor(facts, i, e2):
    """A non-load-bearing role membership for a SECOND entity (variety only;
    never interacts with the candidate's entity)."""
    r = pick(ROLES, "distractor", i)
    facts["meta_types"][r] = "role"
    facts["exists"].append([e2, "S1"])
    facts["holds"].append(["S1", e2, r])


def deep_copy(f):
    return json.loads(json.dumps(f))


# ------------------------------------------------------------- families --
def gen_frig(i):
    """F-RIG rigid persistence. Pair kinds (design §4.4 ex 1):
    i%3==0: base E (propagation)     / companion U (drop existsAt(x,S2))
    i%3==1: base C (propagate+disj)  / companion U (drop acc(S1,S2))
    i%3==2: base E                   / companion C (swap the stated kind)."""
    e = pick(ENTITIES, "frig-e", i)
    e2 = pick([x for x in ENTITIES if x != e], "frig-e2", i)
    k1, k2 = pick2(KINDS, "frig-k", i)
    f = base_facts(e)
    f["meta_types"][k1] = "kind"
    f["exists"] += [[e, "S1"], [e, "S2"]]
    f["holds"].append(["S1", e, k1])
    add_distractor(f, ("frig", i), e2)
    v = i % 3
    if v == 0:
        cand, text = cand_membership("S2", e, k1)
        comp = deep_copy(f)
        comp["exists"] = [p for p in comp["exists"] if p != [e, "S2"]]
        flip = "removed the stated existence of '%s' in S2" % e
    elif v == 1:
        f["meta_types"][k2] = "kind"
        cand, text = cand_membership("S2", e, k2)
        comp = deep_copy(f)
        comp["accessible"] = []
        flip = "removed the accessibility of S2 from S1"
    else:
        f["meta_types"][k2] = "kind"
        cand, text = cand_membership("S2", e, k1)
        comp = deep_copy(f)
        comp["holds"] = [["S1", e, k2] if h == ["S1", e, k1] else h
                         for h in comp["holds"]]
        flip = "swapped the stated kind membership from '%s' to '%s'" % (k1,
                                                                         k2)
    return f, comp, cand, text, flip


def gen_fanti(i):
    """F-ANTI anti-rigid counterworld (design §4.4 ex 2). Necessity claim:
    i%3==0: base C (stated witness)   / companion U (drop the witness)
    i%3==1: base E (holds everywhere) / companion U (drop holds(S2))
    i%3==2: base C (closed scope)     / companion E (add holds(S2))."""
    e = pick(ENTITIES, "fanti-e", i)
    e2 = pick([x for x in ENTITIES if x != e], "fanti-e2", i)
    k = pick(KINDS, "fanti-k", i)
    r = pick(ROLES, "fanti-r", i)
    f = base_facts(e)
    f["meta_types"][k] = "kind"
    f["meta_types"][r] = "role"
    f["exists"] += [[e, "S1"], [e, "S2"]]
    f["holds"] += [["S1", e, k], ["S1", e, r]]
    add_distractor(f, ("fanti", i), e2)
    cand, text = cand_necessity(e, r)
    v = i % 3
    if v == 0:
        f["not_holds"].append(["S2", e, r])
        comp = deep_copy(f)
        comp["not_holds"] = []
        flip = "removed the stated witness non-membership in S2"
    elif v == 1:
        f["holds"].append(["S2", e, r])
        comp = deep_copy(f)
        comp["holds"] = [h for h in comp["holds"] if h != ["S2", e, r]]
        flip = "removed the stated '%s' membership in S2" % r
    else:
        f["closed_for"].append(["S2", r])
        comp = deep_copy(f)
        comp["holds"].append(["S2", e, r])
        flip = "added the stated '%s' membership in S2" % r
    return f, comp, cand, text, flip


def gen_fdisj(i):
    """F-DISJ derived Kind disjointness (design §4.4 ex 3):
    i%3==0: base C (two kinds, zero authored disjointness) /
            companion U ('%s' declared subkind of the first kind instead)
    i%3==1: base E (stated subkind edge upward)   / companion U (drop edge)
    i%3==2: base C                                / companion E (swap the
            stated membership onto the candidate kind — literally stated)."""
    e = pick(ENTITIES, "fdisj-e", i)
    e2 = pick([x for x in ENTITIES if x != e], "fdisj-e2", i)
    k1, k2 = pick2(KINDS, "fdisj-k", i)
    f = base_facts(e)
    f["exists"].append([e, "S1"])
    add_distractor(f, ("fdisj", i), e2)
    v = i % 3
    if v == 0:
        f["meta_types"][k1] = "kind"
        f["meta_types"][k2] = "kind"
        f["holds"].append(["S1", e, k1])
        cand, text = cand_membership("S1", e, k2)
        comp = deep_copy(f)
        comp["subsumptions"].append([k2, k1])
        flip = ("stated '%s' specialises '%s' (subkind-related kinds carry "
                "no derived disjointness)" % (k2, k1))
    elif v == 1:
        sk = pick(SUBKINDS, "fdisj-sk", i)
        parent = SUBKIND_PARENT[sk]
        f["meta_types"][sk] = "subkind"
        f["meta_types"][parent] = "kind"
        f["subsumptions"].append([sk, parent])
        f["holds"].append(["S1", e, sk])
        cand, text = cand_membership("S1", e, parent)
        comp = deep_copy(f)
        comp["subsumptions"] = []
        flip = "removed the stated specialisation edge '%s' -> '%s'" % (
            sk, parent)
    else:
        f["meta_types"][k1] = "kind"
        f["meta_types"][k2] = "kind"
        f["holds"].append(["S1", e, k1])
        cand, text = cand_membership("S1", e, k2)
        comp = deep_copy(f)
        comp["holds"] = [["S1", e, k2] if h == ["S1", e, k1] else h
                         for h in comp["holds"]]
        flip = ("swapped the stated kind membership from '%s' to '%s' "
                "(candidate literally stated)" % (k1, k2))
    return f, comp, cand, text, flip


def gen_fspec(i):
    """F-SPEC rigidity subsumption mask (design §4.4 ex 4):
    i%3==0: base C (illegal kind-under-role edge) / companion E (reversed
            legal edge; candidate follows the edge, design ex 4 companion)
    i%3==1: base C (illegal edge)                 / companion U (drop edge)
    i%3==2: base E (legal role-under-kind edge)   / companion U (drop edge)."""
    e2 = pick(ENTITIES, "fspec-e2", i)
    k = pick(KINDS, "fspec-k", i)
    r = pick(ROLES, "fspec-r", i)
    f = base_facts(None)
    f["meta_types"][k] = "kind"
    f["meta_types"][r] = "role"
    add_distractor(f, ("fspec", i), e2)
    v = i % 3
    if v == 0:
        f["subsumptions"].append([k, r])
        cand, text = cand_spec("S1", k, r)
        comp = deep_copy(f)
        comp["subsumptions"] = [[r, k]]
        comp_cand, comp_text = cand_spec("S1", r, k)
        flip = "reversed the stated specialisation edge to '%s' -> '%s'" % (
            r, k)
        return f, comp, cand, text, flip, (comp_cand, comp_text)
    if v == 1:
        f["subsumptions"].append([k, r])
        cand, text = cand_spec("S1", k, r)
        comp = deep_copy(f)
        comp["subsumptions"] = []
        flip = "removed the stated specialisation edge '%s' -> '%s'" % (k, r)
        return f, comp, cand, text, flip, None
    f["subsumptions"].append([r, k])
    cand, text = cand_spec("S1", r, k)
    comp = deep_copy(f)
    comp["subsumptions"] = []
    flip = "removed the stated specialisation edge '%s' -> '%s'" % (r, k)
    return f, comp, cand, text, flip, None


def gen_oop(i):
    """OUT-OF-PROFILE probes (design §4.4 ex 5): commitments beyond the
    executable inventory. Excluded from the scored slice."""
    e = pick(ENTITIES, "oop-e", i)
    k = pick(KINDS, "oop-k", i)
    f = base_facts(e)
    f["meta_types"][k] = "kind"
    f["exists"] += [[e, "S1"], [e, "S2"]]
    f["holds"].append(["S1", e, k])
    kind3 = ("all-worlds", "identity-criteria", "mereology")[i % 3]
    if kind3 == "all-worlds":
        text = ("'%s' is a '%s' in ALL possible situations whatsoever."
                % (e, k))
    elif kind3 == "identity-criteria":
        text = ("'%s' in S1 and '%s' in S2 are the very same individual by "
                "the identity criteria of '%s'." % (e, e, k))
    else:
        text = ("'%s' is a proper part of situation S1 considered as a "
                "whole." % e)
    cand = {"form": "oop", "oop_kind": kind3}
    return f, cand, text


FAMILIES = {"F-RIG": gen_frig, "F-ANTI": gen_fanti, "F-DISJ": gen_fdisj}


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--out-dir", default=os.path.normpath(
        os.path.join(here, "..", "..", "data", "ufo-sn3-items-v0")))
    ap.add_argument("--pairs-per-family", type=int, default=75)
    ap.add_argument("--oop-probes", type=int, default=30)
    args = ap.parse_args()

    items = []

    def emit(item_id, family, facts, cand, text, scored, pair_id, role,
             flip=None):
        items.append({
            "item_id": item_id, "family": family, "scored": int(scored),
            "pair_id": pair_id, "pair_role": role,
            "near_miss_flip": flip,
            "facts": facts, "candidate": cand,
            "prompt": verbalise(facts, text),
        })

    for fam in ("F-RIG", "F-ANTI", "F-DISJ", "F-SPEC"):
        for i in range(args.pairs_per_family):
            pid = "%s-p%03d" % (fam.lower(), i)
            if fam == "F-SPEC":
                out = gen_fspec(i)
                f, comp, cand, text, flip, comp_cand = out
                emit("%s-base" % pid, fam, f, cand, text, True, pid, "base")
                if comp_cand is not None:
                    ccand, ctext = comp_cand
                else:
                    ccand, ctext = cand, text
                emit("%s-comp" % pid, fam, comp, ccand, ctext, True, pid,
                     "companion", flip)
            else:
                f, comp, cand, text, flip = FAMILIES[fam](i)
                emit("%s-base" % pid, fam, f, cand, text, True, pid, "base")
                emit("%s-comp" % pid, fam, comp, cand, text, True, pid,
                     "companion", flip)
    for i in range(args.oop_probes):
        f, cand, text = gen_oop(i)
        emit("oop-%03d" % i, "OOP", f, cand, text, False, None, None)

    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, "items.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, sort_keys=True, ensure_ascii=False,
                                separators=(",", ":")) + "\n")
    n_scored = sum(it["scored"] for it in items)
    meta = {
        "corpus": "ufo-sn3-items-v0",
        "seed_string": SEED_STRING,
        "generator": "poc/ufo-check-0/gen_items.py",
        "n_items": len(items),
        "n_scored": n_scored,
        "n_oop_probes": len(items) - n_scored,
        "pairs_per_family": args.pairs_per_family,
        "families": ["F-RIG", "F-ANTI", "F-DISJ", "F-SPEC"],
        "note": "gold is NOT in this corpus — engine-derived by "
                "materialise.py (ORACLE-DIAGNOSTIC, PROPOSED-ASM-1481); "
                "balance table lives in the fixtures meta where gold exists",
    }
    with open(os.path.join(args.out_dir, "meta.json"), "w",
              encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote %d items (%d scored, %d OOP probes) -> %s"
          % (len(items), n_scored, len(items) - n_scored, path))


if __name__ == "__main__":
    main()
