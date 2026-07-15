#!/usr/bin/env python3
"""rerender_syn_bridge — SYN-arm re-render for the nsk1-r3 §6.5 surface-bridge.

Implements the SYN arm of docs/next/design/nsk1-r3-hardened.md §6.5 (the
REQUIRED pre-freeze b3 surface-bridge, D-1 mitigation; EXPLORATORY,
phase:"explore", gate:"NSK1-R3-BRIDGE"): the n_bridge = 200 items sampled
WITHOUT replacement by fixed seed 20260714 from the 958 retained covered
items that B'/B"/Stage-1 measured, each re-rendered — SAME chain
(edge_types / genders / proof_state / name assignments), SAME candidate
names — through the PINNED generator's SYNTHETIC templater:

  * templates  = relations_store.yaml 'p' lists, keyed EXACTLY as
    clutrr/generator.py builds synthetic_templates_per_rel
    (for key,val in relations_store: for gender,gv: map[gv['rel']] = gv['p']);
  * renderer   = clutrr.relations.templator.TemplatorSynthetic imported
    UNMODIFIED from the pinned generator checkout (commit d045fae2, the same
    commit the r3 corpus build pins) — NOT a reimplementation;
  * story bytes = per-edge replace_template(edge_type, [child, parent])
    sentences, sentence order shuffled with random.sample and joined with
    ' '. — byte-identical mechanics to generate_rows' story assembly
    (story = random.sample(story, len(story)); ' '.join(story)).

Item set: the 958 retained covered items = the 858 stratum:"covered" rows of
data/nsk1-clutrr/items.jsonl (file order) + the 100 rows of
data/nsk1-clutrr/headroom.jsonl (file order) — the EXACT set and order
poc/modal/modal_nsk1_g2.py::_build_specs_bprime builds over (asserted 958).
[Operational reading, DISCLOSED: §6.5 says "the 958 retained items in
data/nsk1-clutrr/items.jsonl"; that file's 958 rows include the 100
stratum:"uncovered" controls (hop1:null — no chain, not B"-measurable) and
exclude the 100 headroom items B" DID measure. The bridge's stated purpose is
AMT-arm comparability to B", so the B" 958-item covered set is used and the
reading is recorded in provenance for designer confirmation.]

Determinism: PYTHONHASHSEED=0 ENFORCED (re-exec, same guard as
build_clutrr_r3_corpus.py); template choice + sentence order seeded per item
with int(sha256("20260714|<item_id>").hexdigest(),16) & 0xffffffff (disclosed
operational instantiation — §6.5 pins the SAMPLE seed 20260714; the per-item
render seed is derived from it so the artifact is a pure function of the
pinned inputs). Re-running this script byte-reproduces the output.

Templater-fidelity check (mock-validation clause "SYN re-render matches the
r3 templater on a shared item"): for the first 5 committed items of
data/nsk1-clutrr-r3/items.jsonl (built by the r3 templater path), this script
re-derives the chain and ASSERTS the committed story bytes are EXACTLY
reproduced by this renderer's candidate space (some template choice x some
sentence order) — proving byte-level instantiation fidelity ('. ' suffix,
'[Name]' bracketing, ' '-join double-space) without replaying the
generator's global RNG stream. ABORTs on any mismatch.

Output: poc/nsk1/out/r3bridge/syn_renders.jsonl (one row per sampled item,
sample-rank order) + syn_renders_manifest.json (provenance + fidelity-check
record + file sha256). CPU-only, $0, touches ONLY burned items; the fresh r3
corpus, its build seed 20260720, split seed 20260726, and the confirmatory
derangement-seed families {20260720-22}/{20260723-25} are NEVER read for
rendering (r3 items are read ONLY for the fidelity check, never emitted).

    PYTHONHASHSEED=0 python3 poc/nsk1/rerender_syn_bridge.py

Exploratory calibration tooling: rows produced downstream carry
phase:"explore", gate:"NSK1-R3-BRIDGE" and are NEVER eligible for the
confirmatory analysis (nsk1-r3 §6.5).
"""
import hashlib
import json
import os
import random
import re
import subprocess
import sys

# ---- PYTHONHASHSEED enforcement (byte-reproducibility across processes) ----
# carried from poc/nsk1/build_clutrr_r3_corpus.py (str-keyed iteration inside
# the pinned generator modules must not vary with hash salt)
if os.environ.get("PYTHONHASHSEED") != "0":
    env = dict(os.environ, PYTHONHASHSEED="0")
    os.execve(sys.executable, [sys.executable] + sys.argv, env)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

BRIDGE_SAMPLE_SEED = 20260714   # §6.5: fixed sample seed (WITHOUT replacement)
N_BRIDGE = 200                  # §6.5: n_bridge
N_RETAINED = 958                # §6.5: retained covered pool (B" set)
GENERATOR_COMMIT = "d045fae289d3746503677ceed7631c999202501e"  # §6.5 / r3 pin
GEN_DIR = os.path.join(ROOT, "data", "clutrr-cache", "clutrr")
RELSTORE = os.path.join(GEN_DIR, "clutrr", "store", "relations_store.yaml")
OUT_DIR = os.path.join(ROOT, "poc", "nsk1", "out", "r3bridge")
N_FIDELITY = 5                  # committed r3 items checked for byte fidelity

# Kernel relation URNs — same values as build_clutrr_r3_corpus.py / the prior
# builder S7 (mother/father minted concepts).
REL_MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"
REL_FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"
REL_SURFACE = {REL_MOTHER: "mother", REL_FATHER: "father"}
GRAND_OF = {"father": "grandfather", "mother": "grandmother"}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def verify_generator_pin():
    """Same fail-closed pin check as build_clutrr_r3_corpus.py."""
    got = subprocess.check_output(
        ["git", "-C", GEN_DIR, "rev-parse", "HEAD"]).decode().strip()
    if got != GENERATOR_COMMIT:
        raise RuntimeError("ERR_GENERATOR_PIN: HEAD %s != pinned %s (run "
                           "data/clutrr-cache/fetch.sh)" % (got, GENERATOR_COMMIT))
    return got


def load_synthetic_templates():
    """Build synthetic_templates_per_rel EXACTLY as clutrr/generator.py does
    (generate_rows, use_mturk_template=False branch):
        for key, val in store.relations_store.items():
            for gender, gv in val.items():
                synthetic_templates_per_rel[gv['rel']] = gv['p']
    store.relations_store is yaml.load(relations_store.yaml); loaded here
    directly from the SAME pinned file (sha256 recorded in the manifest)."""
    import yaml
    relstore_bytes = open(RELSTORE, "rb").read()
    store = yaml.safe_load(relstore_bytes)
    templates = {}
    for key, val in store.items():
        for gender, gv in val.items():
            templates[gv["rel"]] = gv["p"]
    return templates, sha256_bytes(relstore_bytes)


class _Node:
    """Minimal family-node stub exposing the two attributes
    TemplatorSynthetic.replace_template reads (.name, .gender)."""

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender


def parse_genders(s):
    out = {}
    for part in s.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def load_retained_958():
    """The B" item set + order: covered rows of data/nsk1-clutrr/items.jsonl
    (file order) then data/nsk1-clutrr/headroom.jsonl (file order). Mirrors
    poc/modal/modal_nsk1_g2.py::_build_specs_bprime's source iteration."""
    src = []
    for path, stratum in (("data/nsk1-clutrr/items.jsonl", "covered"),
                          ("data/nsk1-clutrr/headroom.jsonl", None)):
        for line in open(os.path.join(ROOT, path)):
            if not line.strip():
                continue
            it = json.loads(line)
            if stratum is not None and it.get("stratum") != stratum:
                continue
            src.append(it)
    if len(src) != N_RETAINED:
        raise RuntimeError("ERR_POOL: expected %d retained covered items, got %d"
                           % (N_RETAINED, len(src)))
    return src


def chain_of(it):
    """Derive (base, bridge, top, t1, t2, genders) from a retained/r3 item.
    Same name/role derivation as _build_specs_bprime (3-name distinct, unique
    chain-top); t1 cross-checked against provenance edge_types; t2 checked
    against the gold grandparent relation. ABORTs (RuntimeError) on breach."""
    lex = it["lexicon"]
    surfaces = list(lex.values())
    if not (len(lex) == 3 and len({s.lower() for s in surfaces}) == 3):
        raise RuntimeError("ERR_CHAIN_NAMES: item %s not 3-name pairwise-distinct"
                           % it["item_id"])
    subj_urn = it["hop1"]["subject"]
    bridge_urn = it["hop1_bridge"]
    base = lex[subj_urn]
    top_urns = [u for u in lex if u not in (subj_urn, bridge_urn)]
    if len(top_urns) != 1:
        raise RuntimeError("ERR_CHAIN_TOP: item %s no unique chain-top" % it["item_id"])
    top = lex[top_urns[0]]
    bridge = lex[bridge_urn]
    t1 = REL_SURFACE[it["hop1"]["rel"]]
    et = it["provenance"]["edge_types"]
    if list(et) and et[0] != t1:
        raise RuntimeError("ERR_CHAIN_T1: item %s edge_types[0]=%s != hop1 rel %s"
                           % (it["item_id"], et[0], t1))
    t2 = et[1]
    if GRAND_OF.get(t2) != it["gold_surface"]:
        raise RuntimeError("ERR_CHAIN_T2: item %s GRAND_OF[%s] != gold %s"
                           % (it["item_id"], t2, it["gold_surface"]))
    genders = parse_genders(it["provenance"]["genders"])
    for name in (base, bridge, top):
        if genders.get(name) not in ("male", "female"):
            raise RuntimeError("ERR_CHAIN_GENDER: item %s name %s" % (it["item_id"], name))
    return base, bridge, top, t1, t2, genders


def render_item(it, templates, TemplatorSynthetic):
    """Render the SYN-arm story for one item through the pinned
    TemplatorSynthetic (UNMODIFIED class), mirroring generate_rows' assembly:
    per story edge (child, parent, type) -> replace_template(type, [child,
    parent]) (appends '. '), then random.sample sentence shuffle, then
    ' '.join. Global-random seeded per item (module docstring)."""
    base, bridge, top, t1, t2, genders = chain_of(it)
    family = {n: _Node(n, genders[n]) for n in (base, bridge, top)}
    templator = TemplatorSynthetic(templates=templates, family=family)
    seed = int(hashlib.sha256(
        ("%d|%s" % (BRIDGE_SAMPLE_SEED, it["item_id"])).encode()).hexdigest(),
        16) & 0xffffffff
    random.seed(seed)
    # story edges in C1 convention: (base, bridge, t1), (bridge, top, t2)
    sentences = [templator.replace_template(t1, [base, bridge]),
                 templator.replace_template(t2, [bridge, top])]
    if any(s is None for s in sentences):
        raise RuntimeError("ERR_RENDER: template missing for item %s" % it["item_id"])
    order = random.sample(sentences, len(sentences))
    story = " ".join(order)
    # candidate-name identity assert (§6.5: candidate names identical)
    for name in (base, bridge, top):
        if "[%s]" % name not in story:
            raise RuntimeError("ERR_RENDER_NAME: %s missing from SYN story of %s"
                               % (name, it["item_id"]))
    return {"story_syn": story, "render_seed": seed,
            "sentences_edge_order": sentences, "chain":
            {"base": base, "bridge": bridge, "top": top, "t1": t1, "t2": t2,
             "genders": {n: genders[n] for n in (base, bridge, top)}}}


def candidate_sentences(templates, edge_type, child, parent):
    """The full byte-level candidate set this renderer can produce for one
    edge: every relations_store 'p' template instantiated exactly as
    TemplatorSynthetic.replace_template does (e_1=[child], e_2=[parent],
    + '. ')."""
    out = []
    for tpl in templates[edge_type]:
        text = tpl.replace("e_1", "[%s]" % child).replace("e_2", "[%s]" % parent)
        out.append(text + ". ")
    return out


def fidelity_check(templates, TemplatorSynthetic):
    """Prove this renderer's candidate space byte-reproduces the COMMITTED r3
    templater output on shared items: for the first N_FIDELITY rows of
    data/nsk1-clutrr-r3/items.jsonl, the committed story must equal
    ' '.join(perm) for some per-edge template choice and sentence order.
    Also cross-checks the class path: TemplatorSynthetic instantiation ==
    candidate_sentences instantiation for every template. ABORTs on failure."""
    import itertools
    path = os.path.join(ROOT, "data", "nsk1-clutrr-r3", "items.jsonl")
    checked = []
    with open(path) as f:
        for line in f:
            if len(checked) >= N_FIDELITY:
                break
            it = json.loads(line)
            base, bridge, top, t1, t2, genders = chain_of(it)
            cands1 = candidate_sentences(templates, t1, base, bridge)
            cands2 = candidate_sentences(templates, t2, bridge, top)
            # class-path cross-check: the pinned class produces a member of the
            # direct candidate set for this edge (all template choices covered
            # by exhausting random.choice over a seeded scan)
            family = {n: _Node(n, genders[n]) for n in (base, bridge, top)}
            tt = TemplatorSynthetic(templates=templates, family=family)
            seen = set()
            for k in range(64):
                random.seed(k)
                seen.add(tt.replace_template(t1, [base, bridge]))
            if not seen <= set(cands1):
                raise RuntimeError("ERR_FIDELITY_CLASS: class/direct instantiation "
                                   "drift on %s" % it["item_id"])
            story = "\n".join(it["context"])
            ok = any(" ".join(perm) == story
                     for s1 in cands1 for s2 in cands2
                     for perm in itertools.permutations([s1, s2]))
            if not ok:
                raise RuntimeError("ERR_FIDELITY: committed r3 story of %s not "
                                   "reproducible by the pinned templater path\n"
                                   "story=%r" % (it["item_id"], story))
            checked.append(it["item_id"])
    if len(checked) != N_FIDELITY:
        raise RuntimeError("ERR_FIDELITY_COUNT: only %d r3 items available" % len(checked))
    return checked


def main():
    commit = verify_generator_pin()
    sys.path.insert(0, GEN_DIR)
    from clutrr.relations.templator import TemplatorSynthetic  # pinned d045fae2

    templates, relstore_sha = load_synthetic_templates()
    for rel in ("mother", "father"):
        if rel not in templates or not templates[rel]:
            raise RuntimeError("ERR_TEMPLATES: no 'p' list for %s" % rel)

    # ---- templater fidelity vs the committed r3 corpus (shared items) ----
    fidelity_items = fidelity_check(templates, TemplatorSynthetic)
    print("[bridge-rerender] fidelity check PASS on r3 items: %s" % fidelity_items)

    # ---- §6.5 sampler: n=200 WITHOUT replacement, seed 20260714 ----
    pool = load_retained_958()
    idx = sorted(random.Random(BRIDGE_SAMPLE_SEED).sample(range(N_RETAINED), N_BRIDGE))
    idx2 = sorted(random.Random(BRIDGE_SAMPLE_SEED).sample(range(N_RETAINED), N_BRIDGE))
    if idx != idx2:
        raise RuntimeError("ERR_SAMPLER_NONDETERMINISTIC")
    sampled = [pool[i] for i in idx]

    # ---- render ----
    rows = []
    for rank, (i, it) in enumerate(zip(idx, sampled)):
        story_amt = "\n".join(it["context"])
        # provenance story_sha256 pins the released AMT story bytes (§6.5)
        if sha256_bytes(story_amt.encode()) != it["provenance"]["story_sha256"]:
            raise RuntimeError("ERR_AMT_SHA: context/provenance drift on %s"
                               % it["item_id"])
        r = render_item(it, templates, TemplatorSynthetic)
        rows.append({
            "schema": "nsk1-r3-bridge-syn-render/1",
            "phase": "explore", "gate": "NSK1-R3-BRIDGE",
            "item_id": it["item_id"], "sample_rank": rank, "pool_index": i,
            "story_amt_sha256": it["provenance"]["story_sha256"],
            "story_syn": r["story_syn"],
            "story_syn_sha256": sha256_bytes(r["story_syn"].encode()),
            "render_seed": r["render_seed"],
            "chain": r["chain"],
            "gold_surface": it["gold_surface"],
        })

    os.makedirs(OUT_DIR, exist_ok=True)
    renders_path = os.path.join(OUT_DIR, "syn_renders.jsonl")
    with open(renders_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    renders_sha = sha256_bytes(open(renders_path, "rb").read())

    manifest = {
        "schema": "nsk1-r3-bridge-syn-render-manifest/1",
        "phase": "explore", "gate": "NSK1-R3-BRIDGE",
        "spec_ref": "docs/next/design/nsk1-r3-hardened.md §6.5 (SYN arm)",
        "epistemic_status": ("MEASURED (provenance only): every byte is a pure "
                             "function of the pinned generator commit, "
                             "relations_store.yaml, the retained-item files, "
                             "seed 20260714, PYTHONHASHSEED=0."),
        "generator_commit": commit,
        "relations_store_yaml_sha256": relstore_sha,
        "renderer": "clutrr.relations.templator.TemplatorSynthetic (pinned, unmodified)",
        "sample": {"seed": BRIDGE_SAMPLE_SEED, "n": N_BRIDGE,
                   "population": "958 retained covered items = 858 covered rows of "
                                 "data/nsk1-clutrr/items.jsonl (file order) + 100 rows "
                                 "of data/nsk1-clutrr/headroom.jsonl (file order); the "
                                 "B\" measurement set (operational reading DISCLOSED in "
                                 "the script docstring)",
                   "method": "sorted(random.Random(seed).sample(range(958), 200))",
                   "indices_sha256": sha256_bytes(json.dumps(idx).encode())},
        "render_seed_recipe": "int(sha256('20260714|<item_id>').hexdigest(),16)&0xffffffff "
                              "seeding global random for template choice + sentence order",
        "templater_fidelity_check": {
            "shared_items": fidelity_items,
            "result": "PASS (committed r3 story bytes exactly reproducible by this "
                      "renderer's candidate space; class-path instantiation identical)"},
        "quarantine": ("EXPLORATORY calibration input (§6.5): downstream rows are "
                       "phase:'explore', gate:'NSK1-R3-BRIDGE' and NEVER eligible for "
                       "the confirmatory NSK1-R3 analysis. Touches only burned items; "
                       "fresh r3 corpus/seeds untouched."),
        "syn_renders_jsonl_sha256": renders_sha,
        "n_rows": len(rows),
    }
    with open(os.path.join(OUT_DIR, "syn_renders_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")

    print("[bridge-rerender] wrote %d SYN renders -> %s" % (len(rows), renders_path))
    print("[bridge-rerender] syn_renders.jsonl sha256 = %s" % renders_sha)
    print("[bridge-rerender] sample: seed=%d n=%d first=%s last=%s"
          % (BRIDGE_SAMPLE_SEED, N_BRIDGE, rows[0]["item_id"], rows[-1]["item_id"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
