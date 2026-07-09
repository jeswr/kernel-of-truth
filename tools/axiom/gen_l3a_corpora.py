#!/usr/bin/env python3
"""gen_l3a_corpora — deterministic builder of the three L3a corpora:

  data/axioms-v0/   stratum-3 kot-axiom/1 sidecar records (endorsed-axiom layer)
  data/world-v0/    stratum-4 kot-world/1 world-layer records (facts, provenance)
  data/l3a-eval/    the pre-registered eval query set (600 covered + 300 control)

Spec: docs/design-l3a-rules-engine-oracle.md (§2 world layer, §3 axiom set,
§5 eval design). Fully deterministic and RNG-FREE: the corpus is an explicit
enumeration; the registered seed 0 is a placeholder for the pinned generator
constants (documented in the design doc — no stochastic step exists).

EXPECTED ANSWERS are computed from the generator's own construction tables
(parent/maker/part maps built below), NOT by calling the engine — the engine
is the system under test. Residual single-author circularity is registered as
ASM-0006 and is what the cross-vendor audit checks.

Concept URNs are the minted identities of data/kernel-v0/minted-urns.jsonl and
data/molecules-v0/minted-urns.jsonl (stratum 1-2); world-layer entities are
urn:kotw:v0:* identifiers, deliberately OUTSIDE the kernel concept space
(directives §5: facts never enter definitional identity).
"""

import json
import os
import sys

# ------------------------------------------------------------- pinned concepts
# (sourceId -> minted urn, copied verbatim from the minted-urns files; the
#  direction/alias stipulations are registered as ASM-0004)
MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"   # molecules-v0:mother
FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"   # molecules-v0:father
MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"      # molecules-v0:man
WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"    # molecules-v0:woman
BOOKMARK = "urn:kot:bciqg2htlxn4zazdgpx7onf6vwgenwzyvwr3yj7wlv5rt5lge3gcllnq" # kernel-v0:bookmark
MAKER_OF = "urn:kot:bciqkochlqpvvkl2o32wjbosnckrj6jledvvukpxhim6au5rkp2fh3ni" # kernel-v0:maker-of
PART_OF = "urn:kot:bciqen4teyea6c6vjee7kzmd3giqn2r2zgsdtubzbb5bq3o2qrgecggq"  # kernel-v0:part-of
HAS_PART = "urn:kot:bciqpvqb32e3tr2k7uc6z4b5t65kf63khqtuhy6mft7okaip2rl2kfaq" # kernel-v0:has-part
FRIEND = "urn:kot:bciqp6qbwu6plxjo3jnl4jaqhw2dmm5u2y3y26omu2aqrl2pwlilj6fy"   # kernel-v0:friend  (control: NOT in axiom layer)
TEACHER = "urn:kot:bciqetzexanda7yhbp4qzeabkccd4clsu2kex6qwoi3g2pyrlh3kytvy"  # kernel-v0:teacher (control: NOT in axiom layer)

E = "urn:kotw:v0:%s"

# eval strata (pre-registered sizes; instrument asserts them)
COVERED_PLAN = {
    "unique-mother": 122, "unique-father": 122, "children-lookup": 100,
    "unique-maker": 43, "count-maker": 43, "made-lookup": 30,
    "part-lookup": 50, "instance-true": 50, "instance-false-disjoint": 40,
}
CONTROL_PLAN = {
    "out-of-scope-rel": 60, "unknown-entity": 40, "no-record": 60,
    "unlicensed-unique": 40, "unlicensed-count": 30, "conflict": 20,
    "instance-no-record": 20, "malformed": 30,
}


def axiom_records():
    """Stratum 3: the endorsed kot-axiom/1 sidecar set (design doc §3)."""
    return {
        # the maintainer's worked case: mother is a functional (cardinality-1)
        # relation — "who gave birth to Elvis" resolves to a unique lookup
        # (architecture-ladder.md §5). Forward direction = (child -> mother).
        "rel-mother.json": {
            "schema": "kot-axiom/1", "subject": MOTHER,
            "constraints": [{"kind": "functional"},
                            {"kind": "range", "target": WOMAN}]},
        "rel-father.json": {
            "schema": "kot-axiom/1", "subject": FATHER,
            "constraints": [{"kind": "functional"},
                            {"kind": "range", "target": MAN}]},
        # sex disjointness (stipulated classification concepts; the
        # contestability note of design-constraint-layer.md §3.4 applies and is
        # why this is an endorsed sidecar, not concept identity)
        "class-man.json": {
            "schema": "kot-axiom/1", "subject": MAN,
            "constraints": [{"kind": "disjointWith", "target": WOMAN}]},
        # a bookmark has exactly one maker (kernel-v0 litmus family)
        "class-bookmark.json": {
            "schema": "kot-axiom/1", "subject": BOOKMARK,
            "constraints": [{"kind": "cardinality", "path": MAKER_OF,
                             "direction": "inverse", "min": 1, "max": 1}]},
        "rel-maker-of.json": {
            "schema": "kot-axiom/1", "subject": MAKER_OF,
            "constraints": [{"kind": "range", "target": BOOKMARK}]},
        "rel-part-of.json": {
            "schema": "kot-axiom/1", "subject": PART_OF,
            "constraints": [{"kind": "inverseOf", "target": HAS_PART}]},
    }


def build():
    world = []          # kot-world/1 records
    wid = [0]

    def w(rec):
        wid[0] += 1
        rec["id"] = "w%05d" % wid[0]
        world.append(rec)
        return rec["id"]

    def klass(entity, concept, source):
        return w({"schema": "kot-world/1", "kind": "class", "entity": entity,
                  "concept": concept, "provenance": {"source": source}})

    def rel(r, s, o, source):
        return w({"schema": "kot-world/1", "kind": "relation", "relation": r,
                  "subject": s, "object": o, "provenance": {"source": source}})

    SYN = "l3a-synthetic-gen-v0"          # deterministic generator
    PUB = "public-fact-agent-recalled"    # ASM-0005: agent-recalled, not extracted

    # construction tables (ground truth for expected answers)
    mother = {}       # child -> mother
    father = {}
    children_of = {}  # parent -> sorted [children]
    sex = {}          # entity -> MAN|WOMAN (clean entities only)
    maker = {}        # bookmark -> maker      (clean bookmarks)
    made = {}         # maker -> [bookmarks]
    parts = {}        # collection -> [notes]
    whole = {}        # note -> collection
    parentless = []   # persons with no parent records
    planted_conflict_entities = set()

    def add_parents(c, m, f):
        mother[c] = m
        father[c] = f
        children_of.setdefault(m, []).append(c)
        children_of.setdefault(f, []).append(c)
        rel(MOTHER, c, m, SYN if "presley" not in c else PUB)
        rel(FATHER, c, f, SYN if "presley" not in c else PUB)

    # --- Presley anchor family (the maintainer's worked example) ---
    for name, s in (("elvis-presley", MAN), ("gladys-presley", WOMAN),
                    ("vernon-presley", MAN), ("priscilla-presley", WOMAN),
                    ("lisa-marie-presley", WOMAN)):
        sex[E % name] = s
        klass(E % name, s, PUB)
    add_parents(E % "elvis-presley", E % "gladys-presley", E % "vernon-presley")
    add_parents(E % "lisa-marie-presley", E % "priscilla-presley", E % "elvis-presley")
    parentless += [E % "gladys-presley", E % "vernon-presley", E % "priscilla-presley"]

    # --- 30 clean synthetic families, 3 generations, 7 persons each ---
    for i in range(30):
        p = lambda role: E % ("p-f%02d-%s" % (i, role))
        members = {"gf": MAN, "gm": WOMAN, "c1": MAN, "c2": WOMAN,
                   "sp": WOMAN, "g1": MAN, "g2": WOMAN}
        for role in sorted(members):
            sex[p(role)] = members[role]
            klass(p(role), members[role], SYN)
        add_parents(p("c1"), p("gm"), p("gf"))
        add_parents(p("c2"), p("gm"), p("gf"))
        add_parents(p("g1"), p("sp"), p("c1"))
        add_parents(p("g2"), p("sp"), p("c1"))
        parentless += [p("gf"), p("gm"), p("sp")]

    # --- 43 clean bookmarks; makers cycle over family c1 members ---
    for j in range(43):
        b = E % ("bkm-%02d" % j)
        mk = E % ("p-f%02d-c1" % (j % 30))
        klass(b, BOOKMARK, SYN)
        rel(MAKER_OF, mk, b, SYN)
        maker[b] = mk
        made.setdefault(mk, []).append(b)

    # --- 25 part-of pairs (asserted under part-of; has-part via inverseOf) ---
    for j in range(25):
        n, c = E % ("note-%02d" % j), E % ("col-%02d" % j)
        rel(PART_OF, n, c, SYN)
        parts.setdefault(c, []).append(n)
        whole[n] = c

    # --- PLANTED violations (deliberate; controls must refuse ERR_CONFLICT) ---
    # 2 two-mother children (functional violation on mother)
    for j in (1, 2):
        c = E % ("x%d" % j)
        m1, m2, f = (E % ("x%d-m1" % j), E % ("x%d-m2" % j), E % ("x%d-f" % j))
        klass(c, MAN, SYN)
        for m in (m1, m2):
            klass(m, WOMAN, SYN)
            rel(MOTHER, c, m, SYN)
        klass(f, MAN, SYN)
        rel(FATHER, c, f, SYN)
        planted_conflict_entities.update([c, m1, m2])
    # 2 double-maker bookmarks (cardinality max violation)
    for j in (1, 2):
        b = E % ("bkm-x%d" % j)
        mk1, mk2 = E % ("dm-%d" % j), E % "dm-3"
        klass(b, BOOKMARK, SYN)
        for mk in (mk1, mk2):
            if mk not in sex:
                sex[mk] = MAN
                klass(mk, MAN, SYN)
            rel(MAKER_OF, mk, b, SYN)
        planted_conflict_entities.add(b)
    # 1 both-sex entity (disjointness violation)
    bs = E % "bs-1"
    klass(bs, MAN, SYN)
    klass(bs, WOMAN, SYN)
    planted_conflict_entities.add(bs)
    # 1 range violation: mother edge whose object is asserted man
    rc, rcm = E % "rc-child", E % "rc-mother"
    klass(rc, MAN, SYN)
    klass(rcm, MAN, SYN)
    rel(MOTHER, rc, rcm, SYN)
    planted_conflict_entities.update([rc, rcm])

    # ---------------------------------------------------------------- eval set
    queries = []
    qn = [0]

    def q(family, cls, query, expected):
        qn[0] += 1
        queries.append({"qid": "q%04d" % qn[0], "class": cls, "family": family,
                        "query": query, "expected": expected})

    def ans(v):
        return {"kind": "answer", "value": v}

    def ref(code):
        return {"kind": "refuse", "code": code}

    clean_children = sorted(mother)                      # 122 (120 syn + 2 presley)
    clean_mothers = sorted(set(mother.values()))         # 62
    clean_fathers = sorted(set(father.values()))         # 62

    # covered: unique mother/father (122 each; Elvis -> Gladys is q0001)
    order = [E % "elvis-presley"] + [c for c in clean_children if c != E % "elvis-presley"]
    for c in order:
        q("unique-mother", "covered",
          {"op": "unique", "rel": MOTHER, "direction": "forward", "subject": c},
          ans(mother[c]))
    for c in order:
        q("unique-father", "covered",
          {"op": "unique", "rel": FATHER, "direction": "forward", "subject": c},
          ans(father[c]))
    # covered: children lookup via inverse direction (100 of 124 available)
    pool = [(m, MOTHER) for m in clean_mothers] + [(f, FATHER) for f in clean_fathers]
    for parent, r in pool[:100]:
        kids = sorted(k for k in children_of[parent]
                      if (r == MOTHER and mother.get(k) == parent)
                      or (r == FATHER and father.get(k) == parent))
        q("children-lookup", "covered",
          {"op": "lookup", "rel": r, "direction": "inverse", "subject": parent},
          ans(kids))
    # covered: unique maker + exact count (licensed by the bookmark cardinality axiom)
    for b in sorted(maker):
        q("unique-maker", "covered",
          {"op": "unique", "rel": MAKER_OF, "direction": "inverse", "subject": b},
          ans(maker[b]))
    for b in sorted(maker):
        q("count-maker", "covered",
          {"op": "count", "rel": MAKER_OF, "direction": "inverse", "subject": b,
           "qualifier": None}, ans(1))
    # covered: what did this maker make (forward lookup, 30 makers)
    for mk in sorted(made):
        q("made-lookup", "covered",
          {"op": "lookup", "rel": MAKER_OF, "direction": "forward", "subject": mk},
          ans(sorted(made[mk])))
    # covered: part-of both spellings (25 + 25; has-part answered via inverseOf)
    for c in sorted(parts):
        q("part-lookup", "covered",
          {"op": "lookup", "rel": HAS_PART, "direction": "forward", "subject": c},
          ans(sorted(parts[c])))
    for n in sorted(whole):
        q("part-lookup", "covered",
          {"op": "lookup", "rel": PART_OF, "direction": "forward", "subject": n},
          ans([whole[n]]))
    # covered: instance true (50) and instance false-by-disjointness (40)
    clean_persons = sorted(e for e in sex if e not in planted_conflict_entities)
    for e in clean_persons[:50]:
        q("instance-true", "covered",
          {"op": "instance", "entity": e, "concept": sex[e]}, ans(True))
    for e in clean_persons[50:90]:
        other = WOMAN if sex[e] == MAN else MAN
        q("instance-false-disjoint", "covered",
          {"op": "instance", "entity": e, "concept": other}, ans(False))

    # control: out-of-scope relations (friend/teacher are minted kernel concepts
    # but NOT in the axiom layer -> the engine must not pretend to know them)
    for i in range(60):
        r = FRIEND if i % 2 == 0 else TEACHER
        q("out-of-scope-rel", "control",
          {"op": "lookup", "rel": r, "direction": "forward",
           "subject": clean_children[i % len(clean_children)]},
          ref("ERR_TERM_UNLICENSED"))
    # control: unknown entities
    for i in range(40):
        q("unknown-entity", "control",
          {"op": "unique", "rel": MOTHER, "direction": "forward",
           "subject": E % ("ghost-%02d" % i)}, ref("ERR_UNKNOWN_ENTITY"))
    # control: licensed relation, no asserted record (parentless persons)
    for e in sorted(parentless)[:60]:
        q("no-record", "control",
          {"op": "unique", "rel": MOTHER, "direction": "forward", "subject": e},
          ref("ERR_NO_RECORD"))
    # control: unlicensed uniqueness (inverse of functional; forward maker-of)
    for m in clean_mothers[:20]:
        q("unlicensed-unique", "control",
          {"op": "unique", "rel": MOTHER, "direction": "inverse", "subject": m},
          ref("ERR_UNLICENSED_UNIQUE"))
    for mk in sorted(made)[:20]:
        q("unlicensed-unique", "control",
          {"op": "unique", "rel": MAKER_OF, "direction": "forward", "subject": mk},
          ref("ERR_UNLICENSED_UNIQUE"))
    # control: unlicensed count (no exact-cardinality axiom for children)
    for m in clean_mothers[:30]:
        q("unlicensed-count", "control",
          {"op": "count", "rel": MOTHER, "direction": "inverse", "subject": m,
           "qualifier": None}, ref("ERR_UNLICENSED_COUNT"))
    # control: conflict — planted-violation regions must refuse, never resolve (20)
    for j in (1, 2):
        c = E % ("x%d" % j)
        q("conflict", "control", {"op": "unique", "rel": MOTHER, "direction": "forward",
                                  "subject": c}, ref("ERR_CONFLICT"))
        q("conflict", "control", {"op": "lookup", "rel": MOTHER, "direction": "forward",
                                  "subject": c}, ref("ERR_CONFLICT"))
        for mi in (1, 2):
            q("conflict", "control",
              {"op": "lookup", "rel": MOTHER, "direction": "inverse",
               "subject": E % ("x%d-m%d" % (j, mi))}, ref("ERR_CONFLICT"))
    for j in (1, 2):
        b = E % ("bkm-x%d" % j)
        q("conflict", "control", {"op": "unique", "rel": MAKER_OF, "direction": "inverse",
                                  "subject": b}, ref("ERR_CONFLICT"))
        q("conflict", "control", {"op": "count", "rel": MAKER_OF, "direction": "inverse",
                                  "subject": b, "qualifier": None}, ref("ERR_CONFLICT"))
        q("conflict", "control", {"op": "lookup", "rel": MAKER_OF, "direction": "inverse",
                                  "subject": b}, ref("ERR_CONFLICT"))
    q("conflict", "control", {"op": "instance", "entity": bs, "concept": MAN},
      ref("ERR_CONFLICT"))
    q("conflict", "control", {"op": "instance", "entity": bs, "concept": WOMAN},
      ref("ERR_CONFLICT"))
    q("conflict", "control", {"op": "instance", "entity": bs, "concept": BOOKMARK},
      ref("ERR_CONFLICT"))
    q("conflict", "control", {"op": "unique", "rel": MOTHER, "direction": "forward",
                              "subject": rc}, ref("ERR_CONFLICT"))
    q("conflict", "control", {"op": "lookup", "rel": MOTHER, "direction": "forward",
                              "subject": rc}, ref("ERR_CONFLICT"))
    q("conflict", "control", {"op": "lookup", "rel": MAKER_OF, "direction": "forward",
                              "subject": E % "dm-1"}, ref("ERR_CONFLICT"))
    # control: instance with no assertion and no disjointness license
    for j in range(10):
        q("instance-no-record", "control",
          {"op": "instance", "entity": E % ("bkm-%02d" % j), "concept": MAN},
          ref("ERR_NO_RECORD"))
    for j in range(10):
        q("instance-no-record", "control",
          {"op": "instance", "entity": E % ("note-%02d" % j), "concept": BOOKMARK},
          ref("ERR_NO_RECORD"))
    # control: malformed queries
    for j in range(10):
        q("malformed", "control", {"op": "solve", "rel": MOTHER,
                                   "direction": "forward",
                                   "subject": clean_children[j]}, ref("ERR_BAD_QUERY"))
    for j in range(10):
        q("malformed", "control", {"op": "unique", "rel": "mother",
                                   "direction": "forward",
                                   "subject": clean_children[j]}, ref("ERR_BAD_QUERY"))
    for j in range(10):
        q("malformed", "control", {"op": "unique", "rel": MOTHER,
                                   "direction": "sideways",
                                   "subject": clean_children[j]}, ref("ERR_BAD_QUERY"))

    # count-maker queries carry qualifier None -> drop the explicit null (the
    # engine treats absent and null identically; keep records clean JSON)
    for rec in queries:
        if rec["query"].get("qualifier", "sentinel") is None:
            del rec["query"]["qualifier"]

    return world, queries


def main():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    world, queries = build()

    n_cov = sum(1 for r in queries if r["class"] == "covered")
    n_ctl = sum(1 for r in queries if r["class"] == "control")
    fam = {}
    for r in queries:
        fam[r["family"]] = fam.get(r["family"], 0) + 1
    plan = dict(COVERED_PLAN)
    plan.update(CONTROL_PLAN)
    assert n_cov == 600 and n_ctl == 300, (n_cov, n_ctl)
    assert fam == plan, {k: (fam.get(k), plan.get(k)) for k in sorted(set(fam) | set(plan))
                         if fam.get(k) != plan.get(k)}

    ax_dir = os.path.join(root, "data", "axioms-v0")
    os.makedirs(ax_dir, exist_ok=True)
    axs = axiom_records()
    for name in sorted(axs):
        with open(os.path.join(ax_dir, name), "w", encoding="utf-8") as f:
            json.dump(axs[name], f, indent=1, sort_keys=True)
            f.write("\n")
    with open(os.path.join(ax_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"corpus": "axioms-v0", "schema": "kot-axiom/1",
                   "recordCount": len(axs),
                   "stratum": 3,
                   "spec": "docs/design-l3a-rules-engine-oracle.md",
                   "grammar": "docs/design-constraint-layer.md section 3.3",
                   "endorsement": "research-grade, agent-authored; NOT federation-endorsed"},
                  f, indent=1, sort_keys=True)
        f.write("\n")

    w_dir = os.path.join(root, "data", "world-v0")
    os.makedirs(w_dir, exist_ok=True)
    with open(os.path.join(w_dir, "world.jsonl"), "w", encoding="utf-8") as f:
        for rec in world:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    with open(os.path.join(w_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"corpus": "world-v0", "schema": "kot-world/1", "stratum": 4,
                   "recordCount": len(world),
                   "generator": "tools/axiom/gen_l3a_corpora.py (deterministic, RNG-free)",
                   "plantedViolations": {"functional-mother": 2, "card-max-maker": 2,
                                         "disjoint-sex": 1, "range-mother": 1},
                   "spec": "docs/design-l3a-rules-engine-oracle.md"},
                  f, indent=1, sort_keys=True)
        f.write("\n")

    e_dir = os.path.join(root, "data", "l3a-eval")
    os.makedirs(e_dir, exist_ok=True)
    with open(os.path.join(e_dir, "queries.jsonl"), "w", encoding="utf-8") as f:
        for rec in queries:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    with open(os.path.join(e_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"corpus": "l3a-eval", "schema": "kot-query/1-eval",
                   "n_covered": n_cov, "n_control": n_ctl,
                   "strata": plan,
                   "spec": "docs/design-l3a-rules-engine-oracle.md section 5"},
                  f, indent=1, sort_keys=True)
        f.write("\n")

    print(json.dumps({"world_records": len(world), "axiom_records": len(axs),
                      "queries": len(queries), "covered": n_cov, "control": n_ctl,
                      "strata": fam}, indent=1, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
