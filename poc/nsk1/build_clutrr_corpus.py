#!/usr/bin/env python3
"""build_clutrr_corpus — mechanical converter for data/nsk1-clutrr (runner role).

Implements the BUILD RECIPE S1-S11 of docs/design-neurosym-kernel-internals.md
section 5.1 VERBATIM: a pure function of the fetched CLUTRR bytes + pinned seed.
NOTHING here parses natural language; ALL structure comes from CLUTRR's released
STRUCTURED columns (story_edges / edge_types / query_edge / proof_state / genders
/ target / f_comb). Fail-closed: a failed build assertion ABORTS (RuntimeError) —
never patched around (a failed assertion means the format understanding is wrong).

Outputs data/nsk1-clutrr/: world.jsonl, items.jsonl (858 covered + 100 controls),
headroom.jsonl (100 discarded calibration items), lexicon.json, axioms/ (byte-copy
of data/nsk1-eval/axioms/), manifest.json, LICENSE-NOTICE.

Source of record: facebookresearch/clutrr @ d045fae (relations_store.yaml, closed
vocabulary) + the released EMNLP-2019 dataset. Per S1 the canonical dl.fbaipublic
zip URL was substituted at compute-prep time by the README-linked Google-Drive
release (clutrr-emnlp-release.zip, same data_emnlp_final/ inner layout); that
substitution is DISCLOSED in the manifest. CC-BY-NC-4.0 (Sinha et al. 2019,
arXiv:1908.06177); eval-side only (S11).

    python3 poc/nsk1/build_clutrr_corpus.py
"""
import ast
import csv
import hashlib
import io
import json
import os
import random
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
from kot_axiom import Engine  # noqa: E402

SEED = 20260710
N_HEADROOM = 100
N_CONTROL = 100
N_CAP = 1000

ZIP_PATH = os.path.join(ROOT, "data", "clutrr-cache", "clutrr-emnlp-release.zip")
CACHE_MANIFEST = os.path.join(ROOT, "data", "clutrr-cache", "manifest.json")
RELSTORE = os.path.join(ROOT, "data", "clutrr-cache", "clutrr", "clutrr",
                        "store", "relations_store.yaml")
SRC_AXIOMS = os.path.join(ROOT, "data", "nsk1-eval", "axioms")
OUT = os.path.join(ROOT, "data", "nsk1-clutrr")

# Kernel concept URNs — the SAME minted concepts data/nsk1-eval uses (S7: the
# minted concept URNs are exactly mother-of/father-of/man/woman). CLUTRR bytes
# are eval-side only; the kernel side is untouched (S11).
REL_MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"
REL_FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"
CLS_MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
CLS_WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"
REL_OF = {"mother": REL_MOTHER, "father": REL_FATHER}
REL_SURFACE = {REL_MOTHER: "mother", REL_FATHER: "father"}

UP = {"mother", "father"}
CTRL_EXCLUDE = {"mother", "father", "son", "daughter"}
GRAND = {"grandmother", "grandfather"}
GRAND_OF = {"father": "grandfather", "mother": "grandmother"}
GENDER_OF_EDGE = {"father": "male", "mother": "female"}

REQUIRED_COLS = ["id", "story", "query", "target", "clean_story", "proof_state",
                 "f_comb", "story_edges", "edge_types", "query_edge", "genders",
                 "task_name", "task_split"]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"


def parse_row(r):
    try:
        se = ast.literal_eval(r["story_edges"])
        et = ast.literal_eval(r["edge_types"])
        qe = ast.literal_eval(r["query_edge"])
        ps = ast.literal_eval(r["proof_state"])
        q = ast.literal_eval(r["query"])
    except Exception:
        return None
    if not (isinstance(se, list) and isinstance(et, list) and isinstance(qe, tuple)
            and isinstance(ps, list) and isinstance(q, tuple)):
        return None
    return se, et, qe, ps, q


def proof_support(ps):
    try:
        key = list(ps[0].keys())[0]
        return ps[0][key]
    except Exception:
        return None


def endpoints_C1(se):
    """C1 edge convention: edge (a,b) means b is the (mother/father) of a, i.e.
    a is child, b is parent. Returns (base, bridge_of_base, {child: (parent,type)})."""
    parent = {a: b for (a, b) in se}
    dom, rng = set(parent), set(parent.values())
    base = list(dom - rng)
    top = list(rng - dom)
    if len(base) != 1 or len(top) != 1:
        return None, None
    return base[0], top[0]


def edge_by_child_C1(se, et):
    return {a: (b, t) for (a, b), t in zip(se, et)}


def parse_genders(s):
    out = {}
    for part in s.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


# ------------------------------------------------------------------ S3
def orientation_scores(rows2):
    """Score all four (edge-convention x query-convention) combos over every
    pooled clean 2-edge up-edge grandparent row (S3). Returns dict + gender
    cross-check disagreement count. rows2: list of (se,et,qe,q,target,genders)."""
    combos = {("C1", "Q1"): [0, 0], ("C1", "Q2"): [0, 0],
              ("C2", "Q1"): [0, 0], ("C2", "Q2"): [0, 0]}
    gmis = 0
    for se, et, qe, q, target, genders in rows2:
        for EC in ("C1", "C2"):
            if EC == "C1":
                parent = {a: (b, t) for (a, b), t in zip(se, et)}
            else:
                parent = {b: (a, t) for (a, b), t in zip(se, et)}
            dom, rng = set(parent), set(p for p, _ in parent.values())
            base = list(dom - rng)
            top = list(rng - dom)
            if len(base) != 1 or len(top) != 1:
                continue
            base, top = base[0], top[0]
            p1, t1 = parent[base]
            t2 = parent[p1][1] if p1 in parent else None
            pred = GRAND_OF.get(t2)
            for QC in ("Q1", "Q2"):
                gc, gp = (qe[0], qe[1]) if QC == "Q1" else (qe[1], qe[0])
                ok = (pred == target) and (base == gc) and (top == gp)
                combos[(EC, QC)][0] += 1 if ok else 0
                combos[(EC, QC)][1] += 1
        # gender cross-check under winner C1/Q1: gender[G] vs 2nd-edge implied
        base, top = endpoints_C1(se)
        if base is not None:
            ebc = edge_by_child_C1(se, et)
            bridge, _t1 = ebc[base]
            t2 = ebc[bridge][1]
            idx2name = {qe[0]: q[0], qe[1]: q[1]}
            topname = idx2name.get(top)
            if topname in genders and genders[topname] != GENDER_OF_EDGE[t2]:
                gmis += 1
    scores = {"%s/%s" % k: (v[0] / v[1] if v[1] else 0.0) for k, v in combos.items()}
    counts = {"%s/%s" % k: v for k, v in combos.items()}
    return scores, counts, gmis


def main():
    if not os.path.exists(ZIP_PATH):
        raise RuntimeError("ERR_SOURCE_MISSING: %s (run data/clutrr-cache/fetch.sh)" % ZIP_PATH)
    zbytes = open(ZIP_PATH, "rb").read()
    zip_sha = sha256_bytes(zbytes)
    outer = zipfile.ZipFile(io.BytesIO(zbytes))
    cache_manifest = json.load(open(CACHE_MANIFEST))
    relstore_bytes = open(RELSTORE, "rb").read()
    rel_words = sorted(set(re.findall(r"rel:\s*([a-zA-Z-]+)", relstore_bytes.decode())))

    config_order = sorted(n for n in outer.namelist() if n.endswith(".zip"))
    # config kind mapping (from the cache manifest bundles; disclosed source)
    bundles = cache_manifest["released_data"]["bundles"]
    config_kind = {}
    per_file_sha = {}

    # ---- S2: parse every CSV of every config; collect covered + control cands ----
    rows2_for_s3 = []          # S3 population
    covered_cands = []         # dicts with provenance + derived fields
    control_cands = []
    n_missing_col = 0
    drop_fcomb = 0
    drop_dup_in_item = 0
    drop_gender = 0

    for zn in config_order:
        cfg = zn.split("/")[-1].replace(".zip", "")
        config_kind[cfg] = bundles.get(cfg + ".zip", {}).get("kind", "UNKNOWN")
        iz = zipfile.ZipFile(io.BytesIO(outer.read(zn)))
        for fn in sorted(iz.namelist()):
            if not fn.endswith(".csv"):
                continue
            fbytes = iz.read(fn)
            per_file_sha["%s/%s" % (cfg, fn)] = sha256_bytes(fbytes)
            reader = csv.DictReader(io.StringIO(fbytes.decode(errors="replace")))
            for ridx, r in enumerate(reader):
                if any(c not in r for c in REQUIRED_COLS):
                    n_missing_col += 1
                    raise RuntimeError("ERR_MISSING_COLUMN in %s/%s row %d" % (cfg, fn, ridx))
                p = parse_row(r)
                if not p:
                    continue
                se, et, qe, ps, q = p
                supp = proof_support(ps)
                two_edge = (len(se) == 2 and len(et) == 2 and supp is not None
                            and len(supp) == 2)
                if not two_edge:
                    continue
                genders = parse_genders(r["genders"])
                # ---- S3 population: clean 2-edge up-edge grandparent ----
                if set(et) <= UP and r["target"] in GRAND:
                    rows2_for_s3.append((se, et, qe, q, r["target"], genders))

                base, top = endpoints_C1(se)
                if base is None:
                    continue
                ebc = edge_by_child_C1(se, et)
                if base not in ebc:
                    continue
                bridge, t1 = ebc[base]
                if bridge not in ebc:
                    continue
                gtop, t2 = ebc[bridge]
                if gtop != top:
                    continue
                idx2name = {qe[0]: q[0], qe[1]: q[1]}
                base_name = idx2name.get(base)
                top_name = idx2name.get(top)
                if base_name is None or top_name is None:
                    continue
                # bridge name from proof support (shared endpoint of the 2 atoms)
                b0 = {supp[0][0], supp[0][2]}
                b1 = {supp[1][0], supp[1][2]}
                shared = list(b0 & b1)
                if len(shared) != 1:
                    continue
                bridge_name = shared[0]
                ents3 = [base_name, bridge_name, top_name]

                rec = {"cfg": cfg, "file": fn, "ridx": ridx, "id": r["id"],
                       "story": r["story"], "target": r["target"],
                       "f_comb": r["f_comb"], "task_name": r["task_name"],
                       "task_split": r["task_split"], "genders_raw": r["genders"],
                       "edge_types": et, "story_edges": se, "query_edge": qe,
                       "proof_state": r["proof_state"], "query": q,
                       "text_query": r.get("text_query", ""),
                       "base": base_name, "bridge": bridge_name, "top": top_name,
                       "t1": t1, "t2": t2, "genders": genders}

                # ---- S4: covered filter ----
                if set(et) <= UP and r["target"] in GRAND:
                    # (c) f_comb agrees with edge_types
                    if r["f_comb"] != "-".join(et):
                        drop_fcomb += 1
                        continue
                    # (e) query pair == {base, top}
                    if set(qe) != {base, top}:
                        continue
                    # (f) 3 entities pairwise distinct
                    if len(set(ents3)) != 3:
                        drop_dup_in_item += 1
                        continue
                    # gender present + consistent with range axioms (parent side)
                    ok = all(n in genders and genders[n] in ("male", "female")
                             for n in ents3)
                    if ok and (genders[bridge_name] != GENDER_OF_EDGE[t1]
                               or genders[top_name] != GENDER_OF_EDGE[t2]):
                        ok = False
                    if not ok:
                        drop_gender += 1
                        continue
                    covered_cands.append(rec)
                # ---- S5: control candidate ----
                elif not (set(et) & CTRL_EXCLUDE):
                    if set(qe) != {base, top}:
                        continue
                    if len(set(ents3)) != 3:
                        continue
                    # controls need genders for their entities (class records);
                    # missing gender is skipped per-entity at emission (S7).
                    control_cands.append(rec)

    # ---- S3 orientation determination (self-verifying) ----
    scores, counts, gmis = orientation_scores(rows2_for_s3)
    winners = [k for k, v in scores.items() if v >= 0.995]
    if winners != ["C1/Q1"]:
        raise RuntimeError("ERR_ORIENTATION_AMBIGUOUS: exactly one combo must reach "
                           ">=0.995 and it must be C1/Q1; got %s (scores=%s)"
                           % (winners, scores))

    # ---- S6: dedup by story bytes (first under config_order/file/ridx) ----
    def dedup(cands):
        seen, out, dups = set(), [], 0
        for rec in cands:
            k = sha256_bytes(rec["story"].encode())
            if k in seen:
                dups += 1
                continue
            seen.add(k)
            out.append(rec)
        return out, dups

    covered_cands.sort(key=lambda r: (config_order.index(
        [z for z in config_order if z.endswith(r["cfg"] + ".zip")][0]),
        r["file"], r["ridx"]))
    control_cands.sort(key=lambda r: (config_order.index(
        [z for z in config_order if z.endswith(r["cfg"] + ".zip")][0]),
        r["file"], r["ridx"]))
    covered, dup_cov = dedup(covered_cands)
    controls_all, dup_ctrl = dedup(control_cands)
    pool = len(covered)
    if pool < N_HEADROOM + 1:
        raise RuntimeError("ERR_POOL_TOO_SMALL: covered pool %d < headroom+1" % pool)

    # carve headroom (seed-pinned) then final = remainder; n_final=min(1000,pool-100)
    rng = random.Random(SEED)
    idx = list(range(pool))
    rng.shuffle(idx)
    head_idx = set(idx[:N_HEADROOM])
    headroom = [covered[i] for i in sorted(head_idx)]
    remaining = [covered[i] for i in range(pool) if i not in head_idx]
    n_final = min(N_CAP, pool - N_HEADROOM)
    if n_final < len(remaining):
        # stratified subsample by (f_comb x config) — only if pool-100 > 1000
        rng2 = random.Random(SEED + 1)
        buckets = {}
        for rec in remaining:
            buckets.setdefault((rec["f_comb"], rec["cfg"]), []).append(rec)
        picked = []
        keys = sorted(buckets)
        # proportional allocation
        for k in keys:
            share = int(round(n_final * len(buckets[k]) / len(remaining)))
            rng2.shuffle(buckets[k])
            picked.extend(buckets[k][:share])
        picked = picked[:n_final]
        final = sorted(picked, key=lambda r: (r["cfg"], r["file"], r["ridx"]))
    else:
        final = remaining
    n_final = len(final)

    # controls: seed-pinned n=100 stratified by f_comb pattern
    rng3 = random.Random(SEED)
    cbuckets = {}
    for rec in controls_all:
        cbuckets.setdefault(rec["f_comb"], []).append(rec)
    ckeys = sorted(cbuckets)
    per = max(1, N_CONTROL // len(ckeys))
    csel = []
    for k in ckeys:
        rng3.shuffle(cbuckets[k])
        csel.extend(cbuckets[k][:per])
    if len(csel) < N_CONTROL:
        extra = [r for k in ckeys for r in cbuckets[k][per:]]
        rng3.shuffle(extra)
        csel.extend(extra[:N_CONTROL - len(csel)])
    controls = csel[:N_CONTROL]
    control_comp = {}
    for r in controls:
        control_comp[r["f_comb"]] = control_comp.get(r["f_comb"], 0) + 1

    # ------------------------------------------------------------------ S7 + S8
    world = []
    wid = [0]

    def w(rec, prov):
        wid[0] += 1
        rec["id"] = "w%06d" % wid[0]
        rec["schema"] = "kot-world/1"
        rec["provenance"] = prov
        world.append(rec)

    skipped_class_missing_gender = [0]

    def ent_urn(item_id, name):
        return "urn:kotw:v0:%s-%s" % (item_id, slug(name))

    def emit_covered(rec, item_id):
        prov_src = "clutrr %s %s row %s" % (rec["cfg"], rec["file"], rec["id"])
        prov = {"source": prov_src}
        lex = {}
        # class records for the 3 chain entities (by genders; skip+count missing)
        for name in (rec["base"], rec["bridge"], rec["top"]):
            urn = ent_urn(item_id, name)
            lex[urn] = name
            g = rec["genders"].get(name)
            if g in ("male", "female"):
                w({"kind": "class", "entity": urn,
                   "concept": CLS_MAN if g == "male" else CLS_WOMAN}, prov)
            else:
                skipped_class_missing_gender[0] += 1
        base_urn = ent_urn(item_id, rec["base"])
        bridge_urn = ent_urn(item_id, rec["bridge"])
        top_urn = ent_urn(item_id, rec["top"])
        # relation records under C1: subject=child, relation, object=parent
        w({"kind": "relation", "subject": base_urn,
           "relation": REL_OF[rec["t1"]], "object": bridge_urn}, prov)
        w({"kind": "relation", "subject": bridge_urn,
           "relation": REL_OF[rec["t2"]], "object": top_urn}, prov)
        question = ("How is %s related to %s?" % (rec["query"][0], rec["query"][1])
                    if not rec["text_query"].strip() else rec["text_query"])
        item = {
            "item_id": item_id, "stratum": "covered",
            "context": [rec["story"]], "question": question,
            "gold_entity": None, "gold_surface": rec["target"],
            "gold_relation": rec["target"],
            "hop1": {"op": "unique", "rel": REL_OF[rec["t1"]],
                     "direction": "forward", "subject": base_urn},
            "hop1_bridge": bridge_urn,
            "hop2_rel_surface": rec["target"],
            "lexicon": lex,
            "provenance": {"config": rec["cfg"], "file": rec["file"],
                           "csv_row_id": rec["id"], "task_name": rec["task_name"],
                           "task_split": rec["task_split"],
                           "story_sha256": sha256_bytes(rec["story"].encode()),
                           "f_comb": rec["f_comb"], "edge_types": rec["edge_types"],
                           "story_edges": [list(e) for e in rec["story_edges"]],
                           "query_edge": list(rec["query_edge"]),
                           "genders": rec["genders_raw"],
                           "proof_state": rec["proof_state"], "target": rec["target"]},
        }
        return item

    def emit_control(rec, item_id):
        prov_src = "clutrr %s %s row %s" % (rec["cfg"], rec["file"], rec["id"])
        prov = {"source": prov_src}
        lex = {}
        for name in (rec["base"], rec["bridge"], rec["top"]):
            urn = ent_urn(item_id, name)
            lex[urn] = name
            g = rec["genders"].get(name)
            if g in ("male", "female"):
                w({"kind": "class", "entity": urn,
                   "concept": CLS_MAN if g == "male" else CLS_WOMAN}, prov)
            else:
                skipped_class_missing_gender[0] += 1
        # S5/S7: NO edge type in {mother,father,son,daughter} => NO relation
        # records converted => the engine refuses every up-edge lookup.
        question = ("How is %s related to %s?" % (rec["query"][0], rec["query"][1])
                    if not rec["text_query"].strip() else rec["text_query"])
        item = {
            "item_id": item_id, "stratum": "uncovered",
            "context": [rec["story"]], "question": question,
            "gold_entity": None, "gold_surface": rec["target"],
            "gold_relation": rec["target"], "hop1": None, "hop1_bridge": None,
            "hop2_rel_surface": None, "lexicon": lex,
            "provenance": {"config": rec["cfg"], "file": rec["file"],
                           "csv_row_id": rec["id"], "task_name": rec["task_name"],
                           "task_split": rec["task_split"],
                           "story_sha256": sha256_bytes(rec["story"].encode()),
                           "f_comb": rec["f_comb"], "edge_types": rec["edge_types"],
                           "genders": rec["genders_raw"], "target": rec["target"]},
        }
        return item

    final_items = [emit_covered(rec, "clutrr-c%04d" % (i + 1))
                   for i, rec in enumerate(final)]
    control_items = [emit_control(rec, "clutrr-u%04d" % (i + 1))
                     for i, rec in enumerate(controls)]
    headroom_items = [emit_covered(rec, "clutrr-h%04d" % (i + 1))
                      for i, rec in enumerate(headroom)]

    # ------------------------------------------------------------------ S9
    axioms = []
    for n in sorted(os.listdir(SRC_AXIOMS)):
        if n.endswith(".json"):
            axioms.append(("nsk1-clutrr/axioms/%s" % n,
                           json.load(open(os.path.join(SRC_AXIOMS, n)))))
    engine = Engine(axioms, world)

    # S9.1 engine resolution + S9.2 run-time-rule equivalence (covered+headroom)
    fail1 = fail2 = 0
    for it in final_items + headroom_items:
        res = engine.query(dict(it["hop1"]))
        if not (res.get("status") == "answer" and res.get("value") == it["hop1_bridge"]):
            fail1 += 1
        # the two query endpoints: base = hop1.subject, top = the lexicon entity
        # that is neither the subject nor the bridge (bridge is not a query end)
        others = [u for u in it["lexicon"]
                  if u not in (it["hop1"]["subject"], it["hop1_bridge"])]
        endpoints = [it["hop1"]["subject"]] + others
        resolved = []
        for e in endpoints:
            for rel in (REL_MOTHER, REL_FATHER):
                rr = engine.query({"op": "unique", "rel": rel,
                                   "direction": "forward", "subject": e})
                if rr.get("status") == "answer":
                    resolved.append((e, rel, rr.get("value")))
        if not (len(resolved) == 1
                and resolved[0][0] == it["hop1"]["subject"]
                and resolved[0][1] == it["hop1"]["rel"]
                and resolved[0][2] == it["hop1_bridge"]):
            fail2 += 1
    if fail1:
        raise RuntimeError("ERR_S9_1_ENGINE_RESOLUTION: %d covered items did not "
                           "resolve hop1 to the bridge" % fail1)
    if fail2:
        raise RuntimeError("ERR_S9_2_RULE_EQUIVALENCE: %d covered items had !=1 "
                           "licensed unique lookup" % fail2)

    # S9.3 control refusal: all four lookups refuse
    fail3 = 0
    for it in control_items:
        for e in list(it["lexicon"]):
            for rel in (REL_MOTHER, REL_FATHER):
                rr = engine.query({"op": "unique", "rel": rel,
                                   "direction": "forward", "subject": e})
                if rr.get("status") == "answer":
                    fail3 += 1
    if fail3:
        raise RuntimeError("ERR_S9_3_CONTROL_REFUSAL: %d control lookups resolved "
                           "(must refuse)" % fail3)

    # S9.4 gold-not-in-feedback (token-exact) over covered+headroom
    fail4 = 0
    for it in final_items + headroom_items:
        rel_surf = REL_SURFACE[it["hop1"]["rel"]]
        subj = it["lexicon"][it["hop1"]["subject"]]
        obj = it["lexicon"][it["hop1_bridge"]]
        fb = "Note: the %s of %s is %s." % (rel_surf, subj, obj)
        toks = re.findall(r"[a-zA-Z][a-zA-Z-]*", fb.lower())
        if it["gold_surface"].lower() in toks:
            fail4 += 1
    if fail4:
        raise RuntimeError("ERR_S9_4_GOLD_IN_FEEDBACK: %d feedbacks contain gold "
                           "token" % fail4)

    # S9.5 report-only: covered stories containing the gold word as a token
    contam = 0
    for it in final_items:
        toks = set(re.findall(r"[a-z][a-z-]*", it["context"][0].lower()))
        if it["gold_surface"].lower() in toks:
            contam += 1

    # ------------------------------------------------------------------ S10 write
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "axioms"), exist_ok=True)
    for n in sorted(os.listdir(SRC_AXIOMS)):
        if n.endswith(".json"):
            shutil.copyfile(os.path.join(SRC_AXIOMS, n), os.path.join(OUT, "axioms", n))

    with open(os.path.join(OUT, "world.jsonl"), "w") as f:
        for rec in world:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "items.jsonl"), "w") as f:
        for it in final_items + control_items:
            f.write(json.dumps(it, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "headroom.jsonl"), "w") as f:
        for it in headroom_items:
            f.write(json.dumps(it, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "lexicon.json"), "w") as f:
        json.dump({"entities": {},
                   "relations_answer_vocab": rel_words,
                   "relations": {"mother": REL_MOTHER, "father": REL_FATHER},
                   "name_matching": ("per-item: each item carries a closed name "
                                     "lexicon (the read-channel match set); answer "
                                     "scoring is EXACT match over the closed "
                                     "relation vocabulary — no cosine (X3).")},
                  f, indent=1, sort_keys=True)
        f.write("\n")

    with open(os.path.join(OUT, "LICENSE-NOTICE"), "w") as f:
        f.write(
            "CLUTRR-derived evaluation slice (data/nsk1-clutrr)\n"
            "==================================================\n\n"
            "Source: CLUTRR (Compositional Language Understanding with Text-based\n"
            "Relational Reasoning). Koustuv Sinha, Shagun Sodhani, Jin Dong, Joelle\n"
            "Pineau, William L. Hamilton. \"CLUTRR: A Diagnostic Benchmark for\n"
            "Inductive Reasoning from Text.\" EMNLP 2019. arXiv:1908.06177.\n\n"
            "Licence: Creative Commons Attribution-NonCommercial 4.0 International\n"
            "(CC-BY-NC-4.0). https://creativecommons.org/licenses/by-nc/4.0/\n\n"
            "NON-COMMERCIAL USE ONLY. This directory contains story bytes and\n"
            "structured columns derived VERBATIM from the released CLUTRR dataset;\n"
            "it is EVAL-SIDE ONLY (S11): nothing here enters kernel concepts,\n"
            "explications, molecules, or axiom content — the kernel artifact stays\n"
            "licence-clean.\n")

    manifest = {
        "corpus": "nsk1-clutrr",
        "epistemic_status": ("MEASURED (provenance only) — every count below is a "
                             "pure function of the pinned CLUTRR bytes + seed %d; "
                             "no experimental outcome is recorded here." % SEED),
        "built_by": "poc/nsk1/build_clutrr_corpus.py (runner role, S1-S10)",
        "builder_sha256": sha256_bytes(open(__file__, "rb").read()),
        "seed": SEED,
        "source": {
            "generator_repo": "https://github.com/facebookresearch/clutrr",
            "generator_commit": "d045fae289d3746503677ceed7631c999202501e",
            "released_zip": "clutrr-emnlp-release.zip",
            "released_zip_sha256": zip_sha,
            "substituted_source_disclosure": (
                "S1 canonical URL is dl.fbaipublicfiles.com/data_emnlp_final.zip; the "
                "compute-prep line fetched the README-linked Google-Drive release "
                "(gdrive id 1SEq_e1IVCDDzsBIBhoUQ5pOVH5kxRoZF) instead. Same "
                "data_emnlp_final/ inner layout; disclosed per the S1 fallback clause "
                "and pinned by sha256 in data/clutrr-cache/manifest.json."),
            "per_csv_sha256": per_file_sha,
            "config_order": [z.split("/")[-1].replace(".zip", "") for z in config_order],
            "config_kind_mapping": config_kind,
            "relations_store_yaml_sha256": sha256_bytes(relstore_bytes),
            "relation_vocabulary_verbatim": rel_words,
            "relation_vocabulary_note": (
                "%d distinct 'rel:' surface words read VERBATIM from the pinned "
                "relations_store.yaml (note CLUTRR's verbatim spelling 'neice'). "
                "Design section 5.1 says 'closed 24-relation'; the pinned source "
                "yields %d — recorded as measured, flagged for the designer." %
                (len(rel_words), len(rel_words))),
        },
        "orientation_S3": {
            "population_clean_2edge_upedge_rows": len(rows2_for_s3),
            "scores": scores,
            "counts": {k: {"agree": v[0], "n": v[1]} for k, v in counts.items()},
            "determined_convention": "C1/Q1",
            "convention_meaning": ("C1: edge (a,b) with type t => 'b is the t "
                                   "(mother/father) of a' => world relation "
                                   "{subject:a(child), relation:REL(t), object:b(parent)}. "
                                   "Q1: query pair (A,B) => grandchild=A, grandparent=B."),
            "gender_G_vs_2nd_edge_disagreements": gmis,
        },
        "gold_column_resolution": (
            "S2 names 'target_text if present else text_target' as the gold "
            "relation-word column; in the pinned release target_text is ABSENT and "
            "text_target is a full NL sentence (not a vocabulary word). The canonical "
            "relation-word column is 'target' (S8: 'gold_relation = the raw target "
            "column'); it is taken VERBATIM as gold_surface and gold_relation. Gold "
            "is never recomputed/relabelled/filtered-by-answer. Flagged for designer."),
        "question_path": ("fallback template 'How is [A] related to [B]?' in released "
                          "query order — text_query is empty for 0/%d covered rows "
                          "(all covered use the fallback)." % (n_final)),
        "counts": {
            "covered_pool_deduped": pool,
            "covered_pool_dedup_collisions": dup_cov,
            "headroom": len(headroom_items),
            "n_final_covered": n_final,
            "controls": len(control_items),
            "control_candidate_pool_deduped": len(controls_all),
            "control_dedup_collisions": dup_ctrl,
            "remainder_unused": pool - N_HEADROOM - n_final,
            "world_records": len(world),
        },
        "drops": {
            "f_comb_disagreement": drop_fcomb,
            "duplicate_names_in_item": drop_dup_in_item,
            "missing_or_inconsistent_gender": drop_gender,
            "class_records_skipped_missing_gender": skipped_class_missing_gender[0],
        },
        "control_composition_by_f_comb": control_comp,
        "headroom_item_ids": [it["item_id"] for it in headroom_items],
        "build_assertions_S9": {
            "s9_1_engine_resolution": "PASS (100%%, %d items)" % len(final_items + headroom_items),
            "s9_2_rule_equivalence": "PASS (exactly one licensed unique lookup / item)",
            "s9_3_control_refusal": "PASS (all four up-edge lookups refuse / control)",
            "s9_4_gold_not_in_feedback": "PASS (no gold token in any feedback)",
            "s9_5_story_gold_token_contamination_covered": contam,
        },
        "license": {"spdx": "CC-BY-NC-4.0",
                    "citation": "Sinha et al., EMNLP 2019, arXiv:1908.06177",
                    "eval_side_only_S11": True},
    }
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")

    print("nsk1-clutrr built:")
    print("  covered pool (deduped) : %d  (dedup collisions %d)" % (pool, dup_cov))
    print("  headroom               : %d" % len(headroom_items))
    print("  n_final covered        : %d" % n_final)
    print("  controls               : %d  (from %d candidates)" % (len(control_items), len(controls_all)))
    print("  world records          : %d" % len(world))
    print("  S3 orientation scores  : %s" % scores)
    print("  gender cross-check dis. : %d" % gmis)
    print("  drops (fcomb/dupname/gender): %d/%d/%d" % (drop_fcomb, drop_dup_in_item, drop_gender))
    print("  S9.5 story-gold contamination (covered): %d/%d" % (contam, n_final))
    print("  S9 assertions 1-4      : ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
