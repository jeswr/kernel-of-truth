#!/usr/bin/env python3
"""d-casc0 builder — the CASC-0' (STATIC-CASE / M2-isolator) eval corpus.

Design source: docs/next/arch/cascade-synthesis.md §3 ("CASC-0'"), corpus
paragraph verbatim: "the CLUTRR-shaped depth-2-4 engine-derivable generator
from CASC/1 §6, held-out compositions and depths, seed-pinned, self-authored/
covered rider disclosed. n ~ 300-500 base items."  Registry record:
registry/experiments/casc-0.json (DRAFT at authoring time).

WHAT IT EMITS (all deterministic from GENERATOR_SEED; single-draw rule —
a re-draw before freeze requires a correction record, after freeze a new id):

  items/eval.jsonl          n=400 relation-composition items, depths 2/3/4
                            (100/150/150), rank-interleaved so every prefix
                            keeps the depth mix; per item: entities, facts,
                            gold_core/gold_surface, ENGINE-derived
                            intermediate relations (the IR-hard islands),
                            final option set (7 gendered labels, seeded order)
  items/exemplars.jsonl     4 depth-2 exemplar items from the EXEMPLAR path
                            pool (prompt few-shot material; reserved disjoint
                            name pool) — eval items use ONLY the held-out
                            path pool (ERR_HOLDOUT asserted)
  store/facts.jsonl         the AUTHORED STORE: one record per atomic fact
                            (the aligned answer-key analogue the verifier's
                            closure is derived from)
  composition-table.json    the pinned deterministic composition table (the
                            "engine axioms"); every entry carries its
                            stipulated closed-world assumption
  manifest.json             counts, seed, per-file sha256

CLOSED-WORLD STIPULATIONS (PROPOSED-ASM-1143; the composition table is only
sound under them and the generator constructs worlds satisfying them):
full siblings only (all siblings share both parents), no step/half/in-law
relations, no remarriage, all chain entities pairwise distinct persons,
relations are biological, compose() is defined ONLY where the composed
relation is uniquely determined under these assumptions — ambiguous pairs
(e.g. parent-then-child = co-parent) are UNDEFINED and never generated.

SELF-AUTHORED / KERNEL-COVERED RIDER (rides every consuming verdict
sentence): items, store records and all three medium renderings are rendered
from this generator's own authored facts; nothing here is external gold.

Usage:  python3 data/d-casc0/build-dcasc0.py            # build + pin
        python3 data/d-casc0/build-dcasc0.py --check    # verify against manifest
"""

import hashlib
import json
import os
import random
import sys

GENERATOR_SEED = "dcasc0/1|casc-0|20260711"   # pre-committed verbatim in the DRAFT record
N_ITEMS = 400
DEPTH_QUOTA = {2: 100, 3: 150, 4: 150}
N_EXEMPLARS = 4

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Relation algebra. rel(A,B) = "A is the <rel> of B".
# Atomic fact relations (the only relations stated as facts): parent, child,
# sibling. Derived states add: grandparent, grandchild, pibling (aunt/uncle),
# nibling (niece/nephew). compose(r1, r2): rel(A,B)=r1 and rel(B,C)=r2 =>
# rel(A,C) = compose(r1, r2), where defined.
# ---------------------------------------------------------------------------
CORE_TYPES = ["parent", "child", "sibling", "grandparent", "grandchild",
              "pibling", "nibling"]
ATOMIC = ["parent", "child", "sibling"]

# (state, fact) -> new state; every entry names its stipulated justification.
COMPOSE = {
    ("parent", "parent"): "grandparent",    # A parent of B, B parent of C
    ("parent", "sibling"): "parent",        # full-sibling assumption
    ("child", "parent"): "sibling",         # distinct-persons + full siblings
    ("child", "child"): "grandchild",
    ("child", "sibling"): "nibling",        # A child of B, B sibling of C
    ("sibling", "parent"): "pibling",
    ("sibling", "child"): "child",          # full-sibling assumption
    ("sibling", "sibling"): "sibling",      # distinct persons
    ("grandparent", "sibling"): "grandparent",
    ("pibling", "sibling"): "pibling",
    ("nibling", "sibling"): "nibling",
    ("nibling", "child"): "grandchild",     # A's parent and B are children of C
    # UNDEFINED on purpose (ambiguous under the stipulations): (parent,child),
    # (grandparent,parent), (grandparent,child), (grandchild,*), (pibling,
    # parent), (pibling,child), (nibling,parent) — never generated.
}

SURFACE = {  # core relation -> (female, male) surface label
    "parent": ("mother", "father"),
    "child": ("daughter", "son"),
    "sibling": ("sister", "brother"),
    "grandparent": ("grandmother", "grandfather"),
    "grandchild": ("granddaughter", "grandson"),
    "pibling": ("aunt", "uncle"),
    "nibling": ("niece", "nephew"),
}

FEMALE = ["Alice", "Beth", "Carla", "Diane", "Elena", "Fiona", "Grace",
          "Hannah", "Irene", "Julia", "Karen", "Laura", "Mona", "Nadia",
          "Olga", "Paula", "Quinn", "Rosa", "Sara", "Tina", "Uma", "Vera",
          "Wendy", "Xenia", "Yara", "Zoe", "Amber", "Bella", "Clara",
          "Dora", "Edith", "Faye", "Gilda", "Helen", "Iris", "Jane"]
MALE = ["Aaron", "Boris", "Carl", "David", "Edgar", "Felix", "George",
        "Henry", "Ivan", "James", "Kevin", "Louis", "Marco", "Nolan",
        "Oscar", "Peter", "Quentin", "Ralph", "Simon", "Tom", "Ulrich",
        "Victor", "Walter", "Xander", "Yuri", "Zack", "Alan", "Brian",
        "Cedric", "Dylan", "Errol", "Frank", "Gavin", "Hugo", "Isaac",
        "Jonas"]
# reserved DISJOINT exemplar name pool (no eval item uses these)
EX_FEMALE = ["Margot", "Sylvia", "Petra", "Ingrid"]
EX_MALE = ["Rupert", "Casper", "Emil", "Otis"]


def valid_paths(depth):
    """All fact sequences (f1..fd) whose left-fold composition is defined."""
    out = []

    def rec(state, path):
        if len(path) == depth:
            out.append(tuple(path))
            return
        for f in ATOMIC:
            key = (state, f) if state else None
            if state is None:
                rec(f, path + [f])
            elif key in COMPOSE:
                rec(COMPOSE[key], path + [f])
    rec(None, [])
    return out


def fold(path):
    """Engine derivation: the cumulative states s_1..s_d (s_t = rel(X0,Xt))."""
    states = [path[0]]
    for f in path[1:]:
        states.append(COMPOSE[(states[-1], f)])
    return states


def path_key(path):
    return "-".join(path)


def split_holdout(paths2):
    """Deterministic hash split of the depth-2 paths into EXEMPLAR vs EVAL
    pools (held-out compositions); depths 3-4 are eval-only by construction
    (held-out depths: exemplars are depth-2 only)."""
    ex, ev = [], []
    for p in sorted(paths2):
        h = hashlib.sha256(("holdout|%s|%s" % (GENERATOR_SEED, path_key(p)))
                           .encode()).digest()
        (ex if h[0] % 2 == 0 else ev).append(p)
    if not ex or not ev:
        raise SystemExit("ERR_HOLDOUT: degenerate depth-2 path split")
    return ex, ev


def rank_sequence():
    """Largest-remainder interleave of depths so every rank prefix keeps the
    100/150/150 mix (the eval prefix rule consumes a rank prefix)."""
    placed = {d: 0 for d in DEPTH_QUOTA}
    seq = []
    for i in range(N_ITEMS):
        d = max(DEPTH_QUOTA, key=lambda d: (DEPTH_QUOTA[d] - placed[d]) / DEPTH_QUOTA[d]
                if placed[d] < DEPTH_QUOTA[d] else -1.0)
        placed[d] += 1
        seq.append(d)
    assert placed == DEPTH_QUOTA
    return seq


def build_item(rng, item_seq, depth, path, female, male, ns):
    n_ent = depth + 1
    genders = [rng.choice(["F", "M"]) for _ in range(n_ent)]
    f_pool = list(female)
    m_pool = list(male)
    rng.shuffle(f_pool)
    rng.shuffle(m_pool)
    names, fi, mi = [], 0, 0
    for g in genders:
        if g == "F":
            names.append(f_pool[fi]); fi += 1
        else:
            names.append(m_pool[mi]); mi += 1
    item_id = "%s:%05d" % (ns, item_seq)
    entities = [{"urn": "urn:casc0:e:%05d:%d" % (item_seq, i),
                 "label": names[i], "gender": genders[i]}
                for i in range(n_ent)]
    facts = []
    for t, f in enumerate(path):
        subj, obj = entities[t], entities[t + 1]
        facts.append({
            "fact_id": "%s:f%d" % (item_id, t),
            "subj_urn": subj["urn"], "subj_label": subj["label"],
            "obj_urn": obj["urn"], "obj_label": obj["label"],
            "rel_core": f,
            "rel_surface": SURFACE[f][0 if subj["gender"] == "F" else 1],
        })
    states = fold(path)
    gold_core = states[-1]
    g0 = entities[0]["gender"]
    gold_surface = SURFACE[gold_core][0 if g0 == "F" else 1]
    opts = [SURFACE[c][0 if g0 == "F" else 1] for c in CORE_TYPES]
    rng.shuffle(opts)
    keys = [chr(ord("A") + i) for i in range(len(opts))]
    options_final = [{"key": k, "text": t} for k, t in zip(keys, opts)]
    answer = next(o["key"] for o in options_final if o["text"] == gold_surface)
    return {
        "id": item_id,
        "depth": depth,
        "path": list(path),
        "entities": entities,
        "facts": facts,
        # ENGINE-derived cumulative relations rel(X0,Xt) for t=1..d; the
        # runner RE-DERIVES these from facts + composition-table and
        # fail-closes on mismatch (ERR_ENGINE_GOLD). intermediates (the
        # IR-hard islands the verifier checks) are states[1:-1].
        "states_core": states,
        "question_subj": entities[0]["label"],
        "question_obj": entities[-1]["label"],
        "gold_core": gold_core,
        "gold_surface": gold_surface,
        "options_final": options_final,
        "answer": answer,
    }


def build():
    rng = random.Random(int(hashlib.sha256(GENERATOR_SEED.encode())
                            .hexdigest(), 16) % (2 ** 63))
    paths = {d: valid_paths(d) for d in (2, 3, 4)}
    ex2, ev2 = split_holdout(paths[2])
    eval_pool = {2: ev2, 3: sorted(paths[3]), 4: sorted(paths[4])}
    # exemplar paths must never appear as an eval path (held-out compositions)
    for d in eval_pool:
        for p in eval_pool[d]:
            if d == 2 and p in ex2:
                raise SystemExit("ERR_HOLDOUT: exemplar path leaked into eval")

    counters = {2: 0, 3: 0, 4: 0}
    items = []
    for rank, d in enumerate(rank_sequence()):
        pool = eval_pool[d]
        path = pool[counters[d] % len(pool)]
        counters[d] += 1
        it = build_item(rng, len(items), d, path, FEMALE, MALE, "casc0")
        it["rank"] = rank
        items.append(it)

    exemplars = []
    for i in range(N_EXEMPLARS):
        path = ex2[i % len(ex2)]
        ex = build_item(rng, 90000 + i, 2, path, EX_FEMALE, EX_MALE, "casc0x")
        ex["rank"] = i
        exemplars.append(ex)

    ex_paths = {path_key(p) for p in ex2}
    for it in items:
        if path_key(tuple(it["path"])) in ex_paths:
            raise SystemExit("ERR_HOLDOUT: eval item %s uses an exemplar path"
                             % it["id"])

    os.makedirs(os.path.join(HERE, "items"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "store"), exist_ok=True)

    def dump_jsonl(rel, rows):
        p = os.path.join(HERE, rel)
        with open(p, "w") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        return p

    p_items = dump_jsonl(os.path.join("items", "eval.jsonl"), items)
    p_ex = dump_jsonl(os.path.join("items", "exemplars.jsonl"), exemplars)
    store_rows = [f for it in items for f in it["facts"]]
    p_store = dump_jsonl(os.path.join("store", "facts.jsonl"), store_rows)
    table = {"compose": {"%s|%s" % k: v for k, v in sorted(COMPOSE.items())},
             "core_types": CORE_TYPES, "atomic": ATOMIC,
             "surface": {k: list(v) for k, v in SURFACE.items()},
             "semantics": "rel(A,B) = 'A is the <rel> of B'; compose(r1,r2): "
                          "rel(A,B)=r1 & rel(B,C)=r2 => rel(A,C); defined only "
                          "where unique under the stipulated closed world "
                          "(full siblings, no step/in-law, distinct persons)"}
    p_table = os.path.join(HERE, "composition-table.json")
    with open(p_table, "w") as f:
        json.dump(table, f, indent=1, sort_keys=True)
        f.write("\n")

    def sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()

    man = {
        "corpus": "d-casc0",
        "generator_seed": GENERATOR_SEED,
        "n_items": len(items),
        "depth_quota": {str(k): v for k, v in DEPTH_QUOTA.items()},
        "n_exemplars": len(exemplars),
        "n_paths": {str(d): len(paths[d]) for d in paths},
        "n_eval_paths": {str(d): len(eval_pool[d]) for d in eval_pool},
        "exemplar_paths_depth2": sorted(path_key(p) for p in ex2),
        "holdout": "eval depth-2 paths hash-disjoint from exemplar paths; "
                   "depths 3-4 eval-only (exemplars depth-2 only)",
        "files": {
            "items/eval.jsonl": sha(p_items),
            "items/exemplars.jsonl": sha(p_ex),
            "store/facts.jsonl": sha(p_store),
            "composition-table.json": sha(p_table),
        },
        "rider": "SELF-AUTHORED / kernel-covered rider: procedurally generated "
                 "from this builder's own authored facts; gold is "
                 "ENGINE-DERIVED, never external; rides every verdict sentence",
    }
    with open(os.path.join(HERE, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"built": man["files"], "n_items": len(items),
                      "n_exemplars": len(exemplars)}, indent=1))


def check():
    with open(os.path.join(HERE, "manifest.json")) as f:
        man = json.load(f)
    for rel, want in man["files"].items():
        got = hashlib.sha256(open(os.path.join(HERE, rel), "rb").read()).hexdigest()
        if got != want:
            raise SystemExit("ERR_PIN: %s sha %s != manifest %s" % (rel, got, want))
    print("d-casc0 OK: %d files match manifest" % len(man["files"]))


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
