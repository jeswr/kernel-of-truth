#!/usr/bin/env python3
"""gen_nsk1_corpus — deterministic input builder for nsk1 (DRAFT design:
docs/design-neurosym-kernel-internals.md; registry/experiments/nsk1.json).

Builds data/nsk1-eval/:
  axioms/*.json     kot-axiom/1 stratum-3 records (functional mother-of /
                    father-of + man/woman disjointness), copied BY CONTENT from
                    the axioms-v0 semantics (relation/class concept URNs are the
                    SAME minted kernel concepts; this is a NEW corpus with its
                    own pin — the frozen axioms-v0 digest is never touched).
  world.jsonl       kot-world/1 stratum-4 records: N_FAM synthetic 3-generation
                    families (4 grandparents, 2 parents, 2 children), CLEAN
                    (zero planted violations — unlike world-v0).
  items.jsonl       the 2-hop eval: for each child, 4 chains
                    (mother/father ∘ mother/father). Gold label = generator
                    graph traversal — computed HERE, independent of the
                    kot-axiom engine's accept test (the engine only ever
                    resolves/licenses the HOP-1 fact at run time; it never sees
                    or scores the 2-hop gold — the f2b oracle-leakage lesson).
                    Plus N_CONTROL uncovered control items (out-of-scope
                    relation or unknown entity) on which the loop MUST no-op.
  lexicon.json      the closed exact-match surface-form lexicon (entity URN <->
                    unique surface form; relation phrasings). The mapper step in
                    the loop is EXACT match against this — no similarity (X3).
  manifest.json     counts + coverage-by-construction statement + generator pin.

House rules: RNG is seeded explicitly (SEED below); zero runtime deps;
fail-closed (any internal inconsistency raises).
"""
import hashlib
import json
import os
import random
import sys

SEED = 20260710
N_FAM = 140            # 140 families x 2 children x 4 chains = 1120 covered items
N_COVERED = 1000       # pinned subsample
N_CONTROL = 100
N_DISTRACT = 8         # distractor facts from other families per item

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "data", "nsk1-eval")

# Kernel concept URNs — the SAME minted concepts axioms-v0/world-v0 use
# (data/axioms-v0/rel-mother.json etc.); reused so concept identity is shared.
REL_MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"
REL_FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"
CLS_MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
CLS_WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"
REL_SURFACE = {REL_MOTHER: "mother", REL_FATHER: "father"}

GIVEN_F = ["Mara", "Sela", "Odile", "Tessa", "Brina", "Yola", "Nell", "Cora",
           "Dova", "Elin", "Freya", "Gilda", "Hesta", "Ines", "Jorun", "Katya",
           "Lira", "Mina", "Nadia", "Orla", "Petra", "Runa", "Sanna", "Tilda",
           "Ulla", "Vera", "Wanda", "Xena", "Ysolt", "Zelda"]
GIVEN_M = ["Dorin", "Kel", "Bram", "Otto", "Sten", "Varek", "Joss", "Milo",
           "Nedim", "Osric", "Pavel", "Quill", "Rurik", "Soren", "Tomas",
           "Ulric", "Viggo", "Wim", "Xander", "Yorick", "Zed", "Alvar",
           "Boris", "Caspar", "Dmitri", "Egon", "Fenn", "Gustav", "Hale", "Ivo"]
SURNAMES = ["Voss", "Krail", "Mendo", "Tarn", "Ekwe", "Solano", "Brant",
            "Cavel", "Drexa", "Fenmore", "Galt", "Harrow", "Ilvek", "Jasper",
            "Kovan", "Lorne", "Marek", "Norwin", "Oduya", "Prell", "Quist",
            "Rowan", "Sable", "Thane", "Umber", "Vantis", "Weller", "Xylo",
            "Yarrow", "Zeller"]


def slug(name):
    return name.lower().replace(" ", "-")


def main():
    rng = random.Random(SEED)
    os.makedirs(os.path.join(OUT, "axioms"), exist_ok=True)

    # ---- stratum 3: axiom records (content mirrors axioms-v0 semantics) ----
    axioms = {
        "rel-mother.json": {
            "schema": "kot-axiom/1", "subject": REL_MOTHER,
            "constraints": [{"kind": "functional"},
                            {"kind": "range", "target": CLS_WOMAN}]},
        "rel-father.json": {
            "schema": "kot-axiom/1", "subject": REL_FATHER,
            "constraints": [{"kind": "functional"},
                            {"kind": "range", "target": CLS_MAN}]},
        "class-man.json": {
            "schema": "kot-axiom/1", "subject": CLS_MAN,
            "constraints": [{"kind": "disjointWith", "target": CLS_WOMAN}]},
    }
    for name, rec in sorted(axioms.items()):
        with open(os.path.join(OUT, "axioms", name), "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
            f.write("\n")

    # ---- stratum 4: synthetic clean world ----
    world = []
    lexicon = {}      # entity urn -> surface form (unique, exact-match closed set)
    fams = []
    wid = [0]

    def w(rec):
        wid[0] += 1
        rec["id"] = "n%05d" % wid[0]
        rec["schema"] = "kot-world/1"
        rec["provenance"] = {"source": "nsk1-synthetic-generator seed %d" % SEED}
        world.append(rec)

    used_names = set()

    def person(sex, surname):
        pool = GIVEN_F if sex == "f" else GIVEN_M
        for _ in range(1000):
            nm = "%s %s" % (rng.choice(pool), surname)
            if nm not in used_names:
                used_names.add(nm)
                # kot-world/1 entity grammar requires urn:kotw:v0:* (kot_axiom
                # ENTITY_URN_RE); the nsk1- prefix keeps the namespace disjoint
                # from world-v0's ids.
                urn = "urn:kotw:v0:nsk1-%s" % slug(nm)
                lexicon[urn] = nm
                w({"kind": "class", "entity": urn,
                   "concept": CLS_WOMAN if sex == "f" else CLS_MAN})
                return urn
        raise RuntimeError("name pool exhausted")

    for fi in range(N_FAM):
        # unique compound surname per family so surface forms never collide
        sn = "%s-%s" % (SURNAMES[fi % 30], SURNAMES[(fi // 30 + fi) % 30])
        pgm, pgf = person("f", sn), person("m", sn)   # paternal grandparents
        mgm, mgf = person("f", sn), person("m", sn)   # maternal grandparents
        fa, mo = person("m", sn), person("f", sn)     # parents
        c1, c2 = person(rng.choice("fm"), sn), person(rng.choice("fm"), sn)
        rels = [(fa, REL_MOTHER, pgm), (fa, REL_FATHER, pgf),
                (mo, REL_MOTHER, mgm), (mo, REL_FATHER, mgf),
                (c1, REL_MOTHER, mo), (c1, REL_FATHER, fa),
                (c2, REL_MOTHER, mo), (c2, REL_FATHER, fa)]
        for s, r, o in rels:
            w({"kind": "relation", "subject": s, "relation": r, "object": o})
        fams.append({"children": [c1, c2], "fa": fa, "mo": mo,
                     "gp": {("father", "mother"): pgm, ("father", "father"): pgf,
                            ("mother", "mother"): mgm, ("mother", "father"): mgf},
                     "facts": [(s, r, o) for s, r, o in rels]})

    # ---- 2-hop items (gold = traversal here; engine never scores it) ----
    def fact_sentence(s, r, o):
        return "The %s of %s is %s." % (REL_SURFACE[r], lexicon[s], lexicon[o])

    all_facts = [f for fam in fams for f in fam["facts"]]
    items = []
    for fi, fam in enumerate(fams):
        for child in fam["children"]:
            for outer in ("mother", "father"):
                for inner in ("mother", "father"):
                    bridge = fam["fa"] if inner == "father" else fam["mo"]
                    gold = fam["gp"][(inner, outer)]
                    own = [fact_sentence(*f) for f in fam["facts"]]
                    distract = [fact_sentence(*all_facts[rng.randrange(len(all_facts))])
                                for _ in range(N_DISTRACT)]
                    # drop distractors that collide with this family
                    distract = [d for d in distract if d not in own][:N_DISTRACT]
                    ctx = own + distract
                    rng.shuffle(ctx)
                    q = "Who is the %s of the %s of %s?" % (
                        outer, inner, lexicon[child])
                    items.append({
                        "item_id": "nsk1-c%04d" % (len(items) + 1),
                        "stratum": "covered",
                        "context": ctx,
                        "question": q,
                        "gold_entity": gold,
                        "gold_surface": lexicon[gold],
                        # hop-1 spec the LOOP will resolve via the engine at run
                        # time (never the 2-hop answer):
                        "hop1": {"op": "unique",
                                 "rel": REL_MOTHER if inner == "mother" else REL_FATHER,
                                 "direction": "forward", "subject": child},
                        "hop1_bridge": bridge,
                        "hop2_rel_surface": outer,
                    })
    rng.shuffle(items)
    covered = sorted(items[:N_COVERED], key=lambda x: x["item_id"])
    if len(covered) != N_COVERED:
        raise RuntimeError("covered item shortfall: %d" % len(covered))

    # ---- uncovered controls: loop must abstain / no-op ----
    controls = []
    ent_urns = sorted(lexicon)
    for i in range(N_CONTROL):
        fam = fams[rng.randrange(len(fams))]
        child = fam["children"][i % 2]
        if i % 2 == 0:
            q = "Who is the teacher of the %s of %s?" % (
                rng.choice(["mother", "father"]), lexicon[child])   # out-of-scope rel
        else:
            q = "Who is the mother of the father of %s?" % (
                "Prin Undel-%d" % i)                                # unknown entity
        ctx = [fact_sentence(*f) for f in fam["facts"]]
        rng.shuffle(ctx)
        controls.append({"item_id": "nsk1-u%04d" % (i + 1), "stratum": "uncovered",
                         "context": ctx, "question": q,
                         "gold_entity": None, "gold_surface": None,
                         "hop1": None, "hop1_bridge": None,
                         "hop2_rel_surface": None})

    with open(os.path.join(OUT, "world.jsonl"), "w") as f:
        for rec in world:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "items.jsonl"), "w") as f:
        for it in covered + controls:
            f.write(json.dumps(it, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "lexicon.json"), "w") as f:
        json.dump({"entities": lexicon,
                   "relations": {"mother": REL_MOTHER, "father": REL_FATHER}},
                  f, indent=1, sort_keys=True)
        f.write("\n")

    gen_sha = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump({
            "corpus": "nsk1-eval", "seed": SEED,
            "generator": "poc/nsk1/gen_nsk1_corpus.py",
            "generator_sha256": gen_sha,
            "n_world_records": len(world), "n_families": N_FAM,
            "n_covered_items": len(covered), "n_control_items": len(controls),
            "coverage_note": ("Coverage on the covered stratum is BY "
                              "CONSTRUCTION (every relation concept and entity "
                              "in every covered item has kernel/world records "
                              "in this corpus) and is verified by the harness "
                              "coverage gate at run time. This is NOT the m0b "
                              "corpus-indexed coverage number (0.3542 @ "
                              "molecules-v0 on the TinyStories task family, "
                              "one incomplete kernel instance) and extrapolates "
                              "to no other corpus."),
            "gold_independence": ("Gold labels are generator graph-traversal "
                                  "outputs; the kot-axiom engine resolves only "
                                  "hop-1 at run time and never sees or scores "
                                  "the 2-hop gold (f2b oracle-leakage lesson)."),
            "planted_violations": 0,
        }, f, indent=1, sort_keys=True)
        f.write("\n")
    print("nsk1-eval built: %d world records, %d covered, %d control"
          % (len(world), len(covered), len(controls)))


if __name__ == "__main__":
    sys.exit(main())
