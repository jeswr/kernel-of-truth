#!/usr/bin/env python3
"""RULES-2 closure-materialisation pass + c8 train-bytes projection gate.

Design: docs/next/design/rules-2-train-time.md SS2.1/2.2 (PROPOSED-ASM-1421,
1422, 1427, 1431, 1436, 1437) + the RULES-2 build block PROPOSED-ASM-1440..1459
(poc/rules-2/asm-1440-1459.json) + the REWORK-3 block PROPOSED-ASM-1800..
(poc/rules-2/asm-rework3-1800-1813.json) — EMITTED, not registered; this
build never writes registry/assumptions.jsonl.

REWORK-3 (2026-07-12): every cell re-rendered on the RULES-1-C ENTITY FORM
(question 'Who is the <rel> of <base>?' -> object NAME; per-cell 2-option
anti-echo `options`; chance 0.5 DISCLOSED; typing cells keep man/woman) —
the relation-word form this corpus previously carried is measured DEAD for
unaided hosts (docs/next/analysis/rules1b-form-misattribution.md §2). The
c1' derangement is re-derived as the 2-option FORCED FLIP and c8/c4 are
re-derived at chance 0.5 (see PROPOSED-ASM-1801/1803/1804).

WHAT THIS DOES (CPU, deterministic, ~$0 — no GPU, no network, no model):
  build   Materialise the closure of the TRAINING default world — world-v0
          (kinship-inventory records only) + a fresh-seed synthetic expansion
          (nsk1-eval family SHAPE, NEW seed 20260712, NEW name pools, surface
          names asserted disjoint from BOTH eval corpora, fail-closed) — with
          the PINNED RULES-1 twin engine (byte-exact pin verification first;
          ERR_PIN and no output otherwise). Emits data/rules2-train/:
            corpus.jsonl        one example per line: family 1 stated /
                                family 2 entailed {chain E3, cover E1,
                                typing E2} / family 3 refusal E5; each with
                                context lines (RULES-1 canonical
                                verbalisation), ENTITY question, 2-option
                                anti-echo decode set (`options`), NAME (or
                                man/woman or refusal) answer, why() proof
                                sidecar (NEVER in B2 training text; B3
                                only), regime tag (ASM-1162), proof depth,
                                split in {train, sheld, dev}
            c1shuf-map.json     FORCED FLIP of family-2 TRAIN targets to
                                the item's other decode option (c1' at 2
                                options, REWORK-3 PROPOSED-ASM-1803;
                                identical corpus size; per-item assertion
                                shuffled_answer != original_answer holds by
                                construction; anti-correlated, disclosed)
            b1-upsample.json    deterministic cyclic repetition list making
                                |B1| == |B2| (ASM-1425 size matching;
                                PROPOSED-ASM-1447)
            eval-samples.json   pinned eval subsamples: s_mem / s_held /
                                stated_guard / refusal_guard id lists
            manifest.json       counts, seeds, exclusion ledger (NEVER
                                silent), generator sha, split rules
  c8      The train-bytes projection (PROPOSED-ASM-1427; REWORK-3 entity
          form PROPOSED-ASM-1804): the DECONF-A1/GS flat-lookup family
          applied to the PINNED training corpus — a QA index ((base, rel)
          entity question -> trained NAME) plus an aligned fact-line index
          ((base-name, relation-word) -> object NAME), NO joins, NO
          inference. Scores S-out (858 covered nsk1-clutrr, fresh names,
          ENTITY question), S-mem, S-held. GATE G2: S-out recovered
          accuracy must be <= the pinned ceiling or the split is broken =>
          INSTRUMENT-INVALID before any GPU spend. Also emits the c4
          trivial floors re-derived at chance 0.5 (descriptive).

Usage:
  python3 materialise_closure.py build            # real corpus -> data/rules2-train
  python3 materialise_closure.py c8               # gate -> poc/rules-2/results/c8-result.json
  python3 materialise_closure.py build --mock --out-dir /tmp/r2m   # tiny, $0
  python3 materialise_closure.py c8    --mock --out-dir /tmp/r2m   # gate on tiny corpus

HARD RULES: deterministic (explicit seeds only), fail-closed ERR_* codes, no
silent fallbacks; this module states NO feasibility conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_RULES1 = os.path.join(_ROOT, "poc", "rules-1")
sys.path.insert(0, _RULES1)

# ---------------------------------------------------------------------------
# Pins — VERBATIM from the FROZEN registry/experiments/rules-1.json
# (pins.artifact_hashes + pins.corpus_hashes) per PROPOSED-ASM-1437; verified
# BEFORE the pinned engine is imported or a single example is written.
# ---------------------------------------------------------------------------
PIN_TWIN = "399fcd8d946b585e6a73317238e049602ae5e86aef7c4ed1b0243ff887e8dea8"
PIN_RULES_N3 = "9857da8918d8d87823b6d21b248bef83bf5a8515cedeec6ff5dd5c3b26a22f98"
PIN_CERT_RESULT = "e0071e9e4952f915c461206d514afa555d683bc22985fad2273821f37176d379"
PIN_SPARQ_COMMIT = "0ab87b2a5910fe0c783a73dcc043e93ed39c9f58"  # provenance record only
PIN_CORPORA = {
    "world-v0": "dfa5145167b1365681b640f91c766f0a46da28af6941f35a56d00aff35408f9a",
    "nsk1-clutrr": "ede8079b8d59b01da86110ebca0e35d26446a6729a204177ca91aaffd8feac98",
    "nsk1-eval": "5c7c4dfe28cf0c2e131fcb232a8a9cd36132e8fcef9f4e0c2557ab1f7a7b53aa",
    "axioms-v0": "bfcb2f45969b9fe9beb41bcb435d66c078aab3b01d8e6ec387c1bf36b52da718",
    "axioms-kinship-v1": "be3f2d40c1ad06fe7d706c0e36b4f9290d515e798d8e9e2fbb94dc3a02a1508d",
}

SEED_SYN = 20260712       # synthetic-expansion seed (FRESH: != nsk1-eval 20260710)
SEED_SHUF = 20260713      # c1' Sattolo seed over family-2 train targets
N_SYN_FAM = 700           # ~30 examples/family -> ~21k + world-v0 (band 20k-40k)
N_DEV_FAM = 20            # last N synthetic families -> dev split (ASM-1432)
SHELD_FRAC = 0.10         # ASM-1436: pinned 10% held-out entailed cells
EVAL_SAMPLES = {"s_mem": 300, "s_held": 300, "stated_guard": 200,
                "refusal_guard": 150}
C8_SOUT_CEILING = 0.10    # PROPOSED-ASM-1445: G2 ceiling on S-out recovery

REFUSAL_ANSWER = "cannot be determined from these facts"

MOCK = {"n_syn_fam": 12, "n_dev_fam": 2, "n_sout": 60,
        "eval_samples": {"s_mem": 20, "s_held": 20, "stated_guard": 15,
                         "refusal_guard": 10}}

# Fresh name pools — invented, disjoint from the nsk1-eval pools and from the
# CLUTRR given-name surface (asserted fail-closed at build; PROPOSED-ASM-1442).
GIVEN_F2 = ["Aldra", "Bemira", "Cathra", "Dovena", "Elswyn", "Ferrin",
            "Galsa", "Hedvi", "Ilsabet", "Jendra", "Kalvia", "Lorness",
            "Maivi", "Nolwen", "Ostra", "Pellona", "Quilla", "Rhoswen",
            "Sabet", "Talvi", "Undra", "Velsa", "Wrenna", "Xilva",
            "Yavenna", "Zorka", "Brivka", "Cendra", "Dalvina", "Ereska"]
GIVEN_M2 = ["Ardek", "Boruvin", "Caldos", "Drenvik", "Eskil", "Farlan",
            "Gorvin", "Haldek", "Ivenko", "Jorvik", "Kelmar", "Lodvar",
            "Malrik", "Nordvin", "Ovrek", "Palvin", "Quorin", "Rendal",
            "Skarde", "Torvind", "Ulfrik", "Vandor", "Welkin", "Xandrik",
            "Yorven", "Zelvar", "Bramir", "Corvek", "Dalmar", "Ervig"]
SURNAMES2 = ["Varnhem", "Kestrelli", "Moorvane", "Tarnwick", "Eldergrim",
             "Solverin", "Branmoor", "Cavendel", "Drexvale", "Fennwright",
             "Galbrook", "Harwick", "Ilvermore", "Jastrow", "Kovenda",
             "Lorwick", "Marnholt", "Norvale", "Odrassi", "Prellwitz",
             "Quistgard", "Rowntred", "Sablewood", "Thornmere", "Umberley",
             "Vantross", "Wexcombe", "Xylandra", "Yarwood", "Zellenko"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corpus_kot_hash(base):
    """kot-corpus-hash/1 (recipe verbatim from the frozen rules-1 record):
    sha256 over UTF-8 concat of '<sha-of-bytes>  <posix-relpath>\\n' lines,
    two spaces, sorted by relpath UTF-8 byte order; dirs/symlinks excluded."""
    lines = []
    for root, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in files:
            p = os.path.join(root, name)
            if os.path.islink(p):
                continue
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            lines.append((rel, sha256_file(p)))
    blob = "".join("%s  %s\n" % (h, rel)
                   for rel, h in sorted(lines, key=lambda x: x[0].encode()))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def sha_frac(*keys):
    """Deterministic U(0,1) from sha256 over the joined keys (split rule)."""
    h = hashlib.sha256("|".join(str(k) for k in keys).encode()).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


def verify_pins():
    """G1 pin gate (PROPOSED-ASM-1437): byte-exact, fail closed, BEFORE any
    engine import or corpus write. Returns the pin ledger for manifests."""
    checks = {
        "twin_engine.py": (os.path.join(_RULES1, "twin_engine.py"), PIN_TWIN),
        "rules.n3": (os.path.join(_RULES1, "results", "rules.n3"),
                     PIN_RULES_N3),
        "certificate-result.json": (
            os.path.join(_RULES1, "results", "certificate-result.json"),
            PIN_CERT_RESULT),
    }
    ledger = {}
    for name, (path, want) in sorted(checks.items()):
        got = sha256_file(path)
        if got != want:
            raise SystemExit("ERR_PIN: %s sha %s != frozen rules-1 pin %s"
                             % (name, got, want))
        ledger[name] = got
    for corpus, want in sorted(PIN_CORPORA.items()):
        got = corpus_kot_hash(os.path.join(_ROOT, "data", corpus))
        if got != want:
            raise SystemExit("ERR_PIN: data/%s kot-corpus-hash %s != frozen "
                             "rules-1 pin %s" % (corpus, got, want))
        ledger["kot-corpus-hash:" + corpus] = got
    # the pinned PASSED precondition (same flags rules-1 freezes on)
    cert = json.load(open(os.path.join(_RULES1, "results",
                                       "certificate-result.json")))
    cr = cert["certificate_result"]
    if not (cr["success_asm_1131"] and cr["gates_asm_1163_all_pass"]
            and not cr["kill_a_fired"]):
        raise SystemExit("ERR_CERT_PRECONDITION: pinned certificate bytes do "
                         "not carry SUCCESS+gates+no-KILL-a")
    ledger["sparq_commit_recorded"] = PIN_SPARQ_COMMIT
    return ledger


# ---------------------------------------------------------------------------
# Canonical verbalisation — SEMANTICS VERBATIM from poc/rules-1/
# rules1_runner.py verbalise_fact/render_proof (the RULES-1 canonical
# rendering, PROPOSED-ASM-1422); duplicated here so the $0 CPU materialiser
# does not import the GPU-runner module tree. Byte-equivalence of the
# template strings is asserted by the runner at load (ERR_VERBALISER_DRIFT).
# ---------------------------------------------------------------------------
def make_verbaliser(names, urn2word, man_urn, woman_urn):
    def verbalise_fact(f):
        if f[0] == "rel":
            w = urn2word.get(f[2], "related-to")
            return "%s is %s's %s" % (names.get(f[3], f[3]),
                                      names.get(f[1], f[1]), w)
        if f[0] == "cls":
            cw = {man_urn: "man", woman_urn: "woman"}.get(f[2], "person")
            return "%s is a %s" % (names.get(f[1], f[1]), cw)
        return "%s and %s are different people" % (names.get(f[1], f[1]),
                                                   names.get(f[2], f[2]))

    def render_proof(why):
        if why.get("stated"):
            return verbalise_fact(tuple(why["fact"])) + " (stated)"
        prem = "; ".join(render_proof(p) for p in why["premises"])
        return "%s [%s/%s from: %s]" % (verbalise_fact(tuple(why["fact"])),
                                        why["rule"], why["regime"], prem)

    return verbalise_fact, render_proof


def proof_depth(why):
    if why.get("stated"):
        return 0
    return 1 + max((proof_depth(p) for p in why["premises"]), default=0)


def proof_regime(why):
    """Outermost derived rule's regime (ASM-1162 stratification tag)."""
    return None if why.get("stated") else why["regime"]


# ---------------------------------------------------------------------------
# Training default world assembly
# ---------------------------------------------------------------------------
def load_world_v0_components(cert_mod):
    """world-v0 filtered to the RULES-1 closed kinship inventory
    (mother/father relations + man/woman classes). Out-of-inventory records
    (maker-of, part-of, bookmark class) are EXCLUDED AND COUNTED — never
    silently dropped (PROPOSED-ASM-1443). Components over mother/father
    edges; surface name = title-cased URN slug."""
    MOTHER, FATHER = cert_mod.MOTHER, cert_mod.FATHER
    man = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
    woman = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"
    rels, clss, excluded = [], {}, {"relation": 0, "class": 0}
    for line in open(os.path.join(_ROOT, "data", "world-v0", "world.jsonl")):
        r = json.loads(line)
        if r["kind"] == "relation":
            if r["relation"] in (MOTHER, FATHER):
                rels.append((r["subject"], r["relation"], r["object"]))
            else:
                excluded["relation"] += 1
        else:
            if r["concept"] in (man, woman):
                clss[r["entity"]] = r["concept"]
            else:
                excluded["class"] += 1
    adj = {}
    for s, _p, o in rels:
        adj.setdefault(s, set()).add(o)
        adj.setdefault(o, set()).add(s)
    seen, comps = set(), []
    for p in sorted(adj):
        if p in seen:
            continue
        comp, stack = {p}, [p]
        while stack:
            for y in adj[stack.pop()]:
                if y not in comp:
                    comp.add(y)
                    stack.append(y)
        seen |= comp
        ents = sorted(comp)
        names = {u: u.split(":")[-1].replace("-", " ").title() for u in ents}
        comps.append({
            "source": "world-v0", "id": "wv0-%s" % ents[0].split(":")[-1],
            "entities": ents, "names": names,
            "rels": sorted((s, p, o) for s, p, o in rels
                           if s in comp and o in comp),
            "clss": {u: clss[u] for u in ents if u in clss},
        })
    return comps, excluded


def gen_synthetic_components(n_fam, cert_mod, forbidden_names):
    """Fresh-seed synthetic expansion: nsk1-eval family SHAPE (3 generations,
    8 people, 8 gendered-parent edges — poc/nsk1/gen_nsk1_corpus.py), NEW
    seed, NEW name pools (PROPOSED-ASM-1442). Any surface-name collision with
    an eval corpus is fail-closed ERR_NAME_COLLISION."""
    MOTHER, FATHER = cert_mod.MOTHER, cert_mod.FATHER
    man = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
    woman = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"
    for g in GIVEN_F2 + GIVEN_M2 + SURNAMES2:
        if name_collides(g, forbidden_names):
            raise SystemExit("ERR_NAME_COLLISION: name-pool entry %r "
                             "appears in an eval corpus (token-level, "
                             "rework-2)" % g)
    rng = random.Random(SEED_SYN)
    comps, used = [], set()

    def person(sex, surname, names, clsmap):
        pool = GIVEN_F2 if sex == "f" else GIVEN_M2
        for _ in range(1000):
            nm = "%s %s" % (rng.choice(pool), surname)
            if nm not in used:
                if name_collides(nm, forbidden_names):
                    raise SystemExit("ERR_NAME_COLLISION: %r collides with "
                                     "an eval corpus name (token-level, "
                                     "rework-2)" % nm)
                used.add(nm)
                urn = "urn:kotw:v0:r2t-%s" % nm.lower().replace(" ", "-")
                names[urn] = nm
                clsmap[urn] = woman if sex == "f" else man
                return urn
        raise SystemExit("ERR_NAMEPOOL: exhausted")

    for fi in range(n_fam):
        sn = "%s-%s" % (SURNAMES2[fi % 30], SURNAMES2[(fi // 30 + fi) % 30])
        names, clsmap = {}, {}
        pgm = person("f", sn, names, clsmap)
        pgf = person("m", sn, names, clsmap)
        mgm = person("f", sn, names, clsmap)
        mgf = person("m", sn, names, clsmap)
        fa = person("m", sn, names, clsmap)
        mo = person("f", sn, names, clsmap)
        c1 = person(rng.choice("fm"), sn, names, clsmap)
        c2 = person(rng.choice("fm"), sn, names, clsmap)
        rels = [(fa, MOTHER, pgm), (fa, FATHER, pgf),
                (mo, MOTHER, mgm), (mo, FATHER, mgf),
                (c1, MOTHER, mo), (c1, FATHER, fa),
                (c2, MOTHER, mo), (c2, FATHER, fa)]
        comps.append({"source": "syn", "id": "syn-f%04d" % fi,
                      "fam_index": fi, "entities": sorted(names),
                      "names": names, "rels": sorted(rels), "clss": clsmap})
    return comps


def eval_surface_names():
    """All surface names in BOTH eval corpora (nsk1-clutrr item lexicons +
    nsk1-eval lexicon), expanded to TOKEN level — the forbidden set for the
    synthetic expansion and the world-v0 guard. REWORK-2 (cross-vendor
    prereg review 2026-07-12 item 5): the former FULL-NAME-only comparison
    let world-v0 text containing the CLUTRR given names 'Gladys' and 'Lisa'
    (as tokens of 'Gladys Presley' / 'Lisa Marie Presley') into training;
    the disjointness claim (PROPOSED-ASM-1421/1442) is token-level, so the
    guard now is too: every whitespace token of every eval surface name is
    forbidden, and candidate training names are rejected on full-name OR
    token intersection."""
    forb = set()
    for line in open(os.path.join(_ROOT, "data", "nsk1-clutrr",
                                  "items.jsonl")):
        forb.update(json.loads(line)["lexicon"].values())
    lex = json.load(open(os.path.join(_ROOT, "data", "nsk1-eval",
                                      "lexicon.json")))
    for full in lex["entities"].values():
        forb.add(full)
    for full in list(forb):
        forb.update(full.split())
    return forb


def name_collides(surface_name, forbidden):
    """Token-level collision test (PROPOSED-ASM-1442, rework-2): a training
    surface name collides if the full name OR ANY of its whitespace tokens
    appears in the token-expanded forbidden set."""
    return surface_name in forbidden or \
        any(t in forbidden for t in surface_name.split())


# ---------------------------------------------------------------------------
# Example materialisation (one component at a time; local closures only —
# world-v0's planted violations conflict-close their own component and are
# excluded WITH COUNTS, PROPOSED-ASM-1443).
#
# REWORK-3 (PROPOSED-ASM-1800..): every cell is re-rendered on the
# RULES-1-C ENTITY FORM (registry/experiments/rules-1-c.json frozen_sha256
# 09b246dc..., nsk1 g2b form 2 — the ONE form measured inside the host
# capability window; the former relation-word form is recorded
# 'dead-at-floor at every tested host', nsk1-g2d assessment):
#   relation cells: question 'Who is the <rel> of <base>?', answer = the
#   object NAME; per-cell 2-option anti-echo decode set carried in the
#   example's `options` field (both names appear in the cell's context and
#   exclude the base; chance 0.5, DISCLOSED); trained refusal appended at
#   decode time => 3-option decode; NO menu enumeration anywhere.
#   typing cells: unchanged 'Is E a man or a woman?' (already a 2-option
#   forced choice; chance 0.5).
# ENTITY-FORM UNIQUENESS (PROPOSED-ASM-1801): 'Who is the grandmother of
# X?' has TWO true answers in a full 3-generation family, so family-2 chain
# cells restrict their context to the derivation's STATED SUPPORT (proof
# leaves + the support entities' gender facts + UNA over the support) —
# exactly the 3-name two-hop shape of the nsk1-clutrr eval items; the
# unique-answer property is asserted per cell in the restricted closure
# (skipped WITH COUNTS otherwise, never silent). Family-1/3 cells keep the
# full component context (stated mother/father are functional => unique;
# refusals have no licensed answer by construction).
# ---------------------------------------------------------------------------
def component_examples(comp, tbox, cert_mod, Closure, EngineError, vocab4,
                       urn2word, kin_urns, counts):
    MOTHER, FATHER = cert_mod.MOTHER, cert_mod.FATHER
    man = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
    woman = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"
    names = comp["names"]
    verbalise, render = make_verbaliser(names, urn2word, man, woman)
    rel_facts = [("rel", s, p, o) for s, p, o in comp["rels"]]
    cls_facts = [("cls", u, c) for u, c in sorted(comp["clss"].items())]
    una = cert_mod.una(comp["entities"])
    stated = rel_facts + cls_facts + una
    try:
        cl = Closure(tbox, stated)
    except EngineError as e:
        counts["components_engine_error"] += 1
        counts.setdefault("engine_error_codes", []).append(e.code)
        return []
    if cl.conflicts:
        counts["components_conflict_excluded"] += 1
        return []

    def ctx_lines(st):
        rels = [f for f in st if f[0] == "rel"]
        clss = [f for f in st if f[0] == "cls"]
        return [verbalise(f) + "." for f in rels + clss]

    context = ctx_lines(stated)
    ex, eid = [], [0]

    def emit(family, kind, regime, depth, mclass, ctx, q, ans, options,
             proof):
        eid[0] += 1
        ex.append({"id": "r2-%s-%02d" % (comp["id"], eid[0]),
                   "source": comp["source"], "component": comp["id"],
                   "family": family, "kind": kind, "regime": regime,
                   "depth": depth, "menu_class": mclass, "context": ctx,
                   "question": q, "answer": ans, "options": options,
                   "proof_sidecar": proof})

    def q_ent(w, a):
        # RULES-1-C entity question (nsk1 g2b form 2), verbatim template
        return "Who is the %s of %s?" % (w, names[a])

    def unique_object(closure, a, w):
        """The unique x with ('rel', a, vocab4[w], x) in the closure, or
        None when 0 or >1 exist (entity-form uniqueness, ASM-1801)."""
        u = vocab4[w]
        xs = sorted({f[3] for f in closure.facts()
                     if f[0] == "rel" and f[1] == a and f[2] == u})
        return xs[0] if len(xs) == 1 else None

    def sha_pick(tag, eid_str, cands, k=1):
        """Deterministic sha-ordered pick of k candidates (no RNG state)."""
        ranked = sorted(cands, key=lambda nm: hashlib.sha256(
            ("%s|%s|%s" % (tag, eid_str, nm)).encode()).hexdigest())
        return ranked[:k]

    # family 1 — stated cells (format exposure), full component context.
    # Entity form: 'Who is the <w> of <s>?' -> names[o]; anti-echo
    # distractor sha-picked from the component's other surfaces.
    for s, p, o in comp["rels"]:
        try:
            w, why = cl.query_relation(s, o, vocab4)
        except EngineError:
            counts["stated_query_skipped"] += 1
            continue
        if unique_object(cl, s, w) != o:
            counts["entity_ambiguous_skipped"] += 1
            continue
        pool = [names[u] for u in comp["entities"] if u not in (s, o)]
        if not pool:
            counts["entity_no_distractor_skipped"] += 1
            continue
        d = sha_pick("dist", "%s|%s|%s" % (comp["id"], names[s], w), pool)[0]
        emit(1, "stated", None, 0, "name2", context, q_ent(w, s), names[o],
             sorted([names[o], d]), None)

    # family 2 / E3 — entailed relation cells (gendered grandparent chains).
    # Context restricted to the derivation's STATED SUPPORT (ASM-1801):
    # proof leaves + support gender facts + UNA over the support — the
    # 3-name two-hop nsk1 item shape; options = {bridge, chain-top}
    # (anti-echo structural, byte-matching the rules-1-c eval decode).
    def support_leaves(why):
        leaves = set()

        def walk(n):
            if n.get("stated"):
                leaves.add(tuple(n["fact"]))
            else:
                for pr in n["premises"]:
                    walk(pr)
        walk(why)
        return leaves

    stated_rel_set = set(rel_facts)
    refusable_pairs = []
    for a in comp["entities"]:
        for b in comp["entities"]:
            if a == b or ("rel", a, MOTHER, b) in stated_rel_set \
                    or ("rel", a, FATHER, b) in stated_rel_set:
                continue
            try:
                w, why = cl.query_relation(a, b, vocab4)
            except EngineError as e:
                if e.code == "ERR_INSUFFICIENT_PREMISES":
                    refusable_pairs.append((a, b))
                continue
            if why.get("stated"):
                continue
            leaves = support_leaves(why)
            ents = set()
            for f in leaves:
                if f[0] == "rel":
                    ents.update((f[1], f[3]))
                elif f[0] == "cls":
                    ents.add(f[1])
            if len(ents) != 3:
                # not the two-hop 3-name shape — no anti-echo bridge option
                counts["entity_support_not3_skipped"] += 1
                continue
            st2 = sorted(f for f in leaves if f[0] == "rel") + \
                [("cls", u, comp["clss"][u]) for u in sorted(ents)
                 if u in comp["clss"]] + cert_mod.una(sorted(ents))
            try:
                cl2 = Closure(tbox, st2)
                w2, why2 = cl2.query_relation(a, b, vocab4)
            except EngineError:
                counts["entity_support_closure_skipped"] += 1
                continue
            if w2 != w:
                raise SystemExit("ERR_SUPPORT_DRIFT: %s->%s %r != %r in the "
                                 "support-restricted closure" % (a, b, w2, w))
            if unique_object(cl2, a, w) != b:
                counts["entity_ambiguous_skipped"] += 1
                continue
            bridge = next(iter(ents - {a, b}))
            emit(2, "chain", proof_regime(why2), proof_depth(why2), "name2",
                 ctx_lines(st2), q_ent(w, a), names[b],
                 sorted([names[b], names[bridge]]), render(why2))

    # family 2 / E1 — cover-elimination cells (held-out gendered edge
    # abstracted to `parent`; certificate.build_e1_cells construction).
    # Entity form: 'Who is the <held-gender-word> of <c>?' -> names[held];
    # options = the two parents (both in context, base excluded).
    parent_urn = kin_urns["parent"]
    mo_of = {s: o for s, p, o in comp["rels"] if p == MOTHER}
    fa_of = {s: o for s, p, o in comp["rels"] if p == FATHER}
    for c in sorted(set(mo_of) & set(fa_of)):
        m, f = mo_of[c], fa_of[c]
        if m == f:
            continue
        for held, kept_rel, kept_obj, gold in (
                (f, MOTHER, m, "father"), (m, FATHER, f, "mother")):
            st2 = [("rel", c, kept_rel, kept_obj),
                   ("rel", c, parent_urn, held)] + \
                  [("cls", u, comp["clss"][u]) for u in sorted({c, m, f})
                   if u in comp["clss"]] + cert_mod.una([c, m, f])
            try:
                cl2 = Closure(tbox, st2)
                w, why = cl2.query_relation(c, held, vocab4)
            except EngineError:
                counts["e1_cell_skipped"] += 1
                continue
            if w != gold:
                raise SystemExit("ERR_E1_GOLD: engine %r != held-out %r"
                                 % (w, gold))
            if unique_object(cl2, c, gold) != held:
                counts["entity_ambiguous_skipped"] += 1
                continue
            emit(2, "cover", proof_regime(why), proof_depth(why), "name2",
                 ctx_lines(st2), q_ent(gold, c), names[held],
                 sorted([names[held], names[kept_obj]]), render(why))

    # family 2 / E2 — domain/range typing cells (one gender class fact
    # abstracted away; recovered via range(mother)/range(father)).
    # Already a 2-option forced choice (chance 0.5) — form unchanged.
    done = set()
    for want_rel, want_word in ((MOTHER, "woman"), (FATHER, "man")):
        for s, p, o in comp["rels"]:
            if p != want_rel or o in done or o not in comp["clss"]:
                continue
            st2 = [f for f in stated if f != ("cls", o, comp["clss"][o])]
            cl2 = Closure(tbox, st2)
            cls_urn = woman if want_word == "woman" else man
            fact = ("cls", o, cls_urn)
            if fact not in cl2.facts() or cl2.deriv.get(fact) is None:
                counts["e2_cell_skipped"] += 1
                continue
            why = cl2.why(fact)
            emit(2, "typing", proof_regime(why), proof_depth(why), "mw2",
                 ctx_lines(st2), "Is %s a man or a woman?" % names[o],
                 want_word, ["man", "woman"], render(why))
            done.add(o)
            break  # one typing cell per gender per component

    # family 3 / E5 — insufficient-premise refusal cells (TRAINED and
    # SCORED, PROPOSED-ASM-1431). Entity form: (base, rel) queries with NO
    # licensed object anywhere in the component closure ('Who is the
    # grandmother of <a top-generation person>?'); the pair-refusability
    # ledger keeps the engine-refusal assertion. Options = two sha-picked
    # non-base surfaces (the refusal target is appended at decode time).
    ref_cands = []
    for a in comp["entities"]:
        for w in sorted(vocab4):
            u = vocab4[w]
            if any(f[0] == "rel" and f[1] == a and f[2] == u
                   for f in cl.facts()):
                continue
            ref_cands.append((a, w))
    ref_cands.sort(key=lambda aw: hashlib.sha256(
        ("ref|%s|%s|%s" % (comp["id"], names[aw[0]], aw[1])).encode())
        .hexdigest())
    n_ref = 0
    for a, w in ref_cands:
        if n_ref >= 4:
            break
        pool = [names[u] for u in comp["entities"] if u != a]
        if len(pool) < 2:
            counts["refusal_cell_skipped"] += 1
            continue
        opts = sorted(sha_pick("refopt", "%s|%s|%s" % (comp["id"], names[a],
                                                       w), pool, k=2))
        emit(3, "refusal", None, 0, "name2", context, q_ent(w, a),
             REFUSAL_ANSWER, opts, None)
        n_ref += 1
    if refusable_pairs and n_ref == 0:
        counts["refusal_cell_skipped"] += 1
    return ex


def build(args):
    pins = verify_pins()
    from twin_engine import Closure, EngineError, load_tbox  # noqa: E402
    import certificate as cert_mod  # noqa: E402

    kin = json.load(open(os.path.join(_ROOT, "data", "axioms-kinship-v1",
                                      "manifest.json")))
    u = kin["minted_urns"]
    # query vocab: the four gendered answer words — SAME closed answer set the
    # pinned certificate and rules-1 use (parent/grandparent are urn2word-only)
    vocab4 = {"mother": cert_mod.MOTHER, "father": cert_mod.FATHER,
              "grandfather": u["grandfather"], "grandmother": u["grandmother"]}
    urn2word = {v: k for k, v in vocab4.items()}
    urn2word[u["parent"]] = "parent"
    urn2word[u["grandparent"]] = "grandparent"
    tbox = load_tbox(cert_mod.TBOX_PINNED)

    n_fam = MOCK["n_syn_fam"] if args.mock else N_SYN_FAM
    n_dev = MOCK["n_dev_fam"] if args.mock else N_DEV_FAM
    forb = eval_surface_names()
    comps = load_world_v0_components(cert_mod)
    wv0_comps, wv0_excluded = comps
    syn_comps = gen_synthetic_components(n_fam, cert_mod, forb)
    # world-v0 surface-name collision guard: exclude + count (real names are
    # outside our control; exclusion is deterministic and disclosed).
    # REWORK-2 (review item 5): the test is TOKEN-level — full-name-only
    # matching admitted 'Gladys Presley'/'Lisa Marie Presley' although
    # 'Gladys' and 'Lisa' are CLUTRR item-lexicon names. Excluded component
    # ids are listed, not just counted.
    wv0_kept = []
    counts = {"components_conflict_excluded": 0,
              "components_engine_error": 0, "stated_query_skipped": 0,
              "e1_cell_skipped": 0, "e2_cell_skipped": 0,
              "refusal_cell_skipped": 0,
              "entity_ambiguous_skipped": 0,
              "entity_no_distractor_skipped": 0,
              "entity_support_not3_skipped": 0,
              "entity_support_closure_skipped": 0,
              "wv0_name_collision_excluded": 0,
              "wv0_name_collision_excluded_ids": [],
              "wv0_out_of_inventory_records": wv0_excluded}
    for c in wv0_comps:
        if any(name_collides(n, forb) for n in c["names"].values()):
            counts["wv0_name_collision_excluded"] += 1
            counts["wv0_name_collision_excluded_ids"].append(c["id"])
            continue
        wv0_kept.append(c)

    examples = []
    for comp in wv0_kept + syn_comps:
        examples.extend(component_examples(
            comp, tbox, cert_mod, Closure, EngineError, vocab4, urn2word,
            u, counts))

    # splits (PROPOSED-ASM-1444): dev = last N_DEV synthetic families;
    # sheld = pinned sha-rule 10% of non-dev family-2 cells
    dev_fams = {"syn-f%04d" % i for i in range(n_fam - n_dev, n_fam)}
    for e in examples:
        if e["component"] in dev_fams:
            e["split"] = "dev"
        elif e["family"] == 2 and sha_frac("sheld", e["id"]) < SHELD_FRAC:
            e["split"] = "sheld"
        else:
            e["split"] = "train"

    train2 = [e for e in examples if e["split"] == "train" and e["family"] == 2]
    train13 = [e for e in examples
               if e["split"] == "train" and e["family"] in (1, 3)]
    sheld = [e for e in examples if e["split"] == "sheld"]

    # c1' derangement of family-2 TRAIN targets — REWORK-3 re-derivation at
    # the 2-option ENTITY surface (PROPOSED-ASM-1803; supersedes the rework-2
    # label-block rotation, which presupposed a shared 23-word label space):
    # entity targets are PER-ITEM NAMES from the item's own family, so no
    # cross-item label permutation is well-defined. At exactly 2 candidate
    # options the ONLY derangement is the FORCED FLIP: every family-2 train
    # target is replaced by the item's OTHER decode option (the anti-echo
    # distractor; man<->woman for typing cells). Properties, DISCLOSED:
    #   * shuffled_answer != original_answer holds for EVERY item BY
    #     CONSTRUCTION (the rework-1 per-item operative requirement);
    #   * token cost preserved up to name-length variation (both options
    #     appear in the item's own context);
    #   * the control is ANTI-CORRELATED, not merely decorrelated — it
    #     trains the complement rule ('answer the bridge'), a STRONGER
    #     content destruction than a shuffle; s1' recovery < 0.30 remains
    #     the registered test and a negative c1p lift counts as recovery
    #     ~0, never a pass of the primary;
    #   * CAVEAT (shortcut coverage, PROPOSED-ASM-1806): because the flip
    #     teaches 'pick the bridge', a c1p collapse CANNOT separate
    #     content-driven lift from a learned positional/anti-bridge
    #     shortcut; that residual confound is a registered DESIGN-OPEN for
    #     the pre-freeze review gate, argued (not resolved) in the ASM.
    shuf_map, shuf_disclosure = {}, {}
    for mclass in sorted({e["menu_class"] for e in train2}):
        cls_items = sorted((e for e in train2 if e["menu_class"] == mclass),
                           key=lambda e: e["id"])
        if len(cls_items) < 2:
            raise SystemExit("ERR_SHUFFLE: <2 items in class %s" % mclass)
        for e in cls_items:
            opts = e["options"]
            if len(opts) != 2 or e["answer"] not in opts:
                raise SystemExit("ERR_SHUFFLE: %s options %r do not contain "
                                 "the answer exactly once at 2 options"
                                 % (e["id"], opts))
            shuf_map[e["id"]] = next(o for o in opts if o != e["answer"])
        # PER-ITEM assertion (the rework-1 operative requirement)
        orig = {e["id"]: e["answer"] for e in cls_items}
        bad = [e["id"] for e in cls_items
               if shuf_map[e["id"]] == orig[e["id"]]]
        if bad:
            raise SystemExit("ERR_SHUFFLE: %d label-correct target(s) remain"
                             " in class %s (first: %s)"
                             % (len(bad), mclass, bad[0]))
        shuf_disclosure[mclass] = {
            "n": len(cls_items), "construction": "forced flip to the other "
            "2-option decode candidate (entity form; REWORK-3)",
            "note": "anti-correlated by construction (trains the complement "
                    "rule); per-item shuffled != original holds for all "
                    "items; token cost preserved up to name-length "
                    "variation; shortcut-coverage caveat disclosed "
                    "(PROPOSED-ASM-1806)"}

    # B1 size matching (ASM-1425 / PROPOSED-ASM-1447): deterministic cyclic
    # repetition of stated+refusal train ids until |B1| == |B2|
    need = len(train2)
    base_ids = sorted(e["id"] for e in train13)
    upsample = [base_ids[i % len(base_ids)] for i in range(need)]

    # pinned eval subsamples (sha-sorted, first-K)
    sizes = MOCK["eval_samples"] if args.mock else EVAL_SAMPLES
    by_sha = lambda es, tag: sorted(es, key=lambda e: sha_frac(tag, e["id"]))
    eval_samples = {
        "s_mem": [e["id"] for e in by_sha(train2, "smem")[:sizes["s_mem"]]],
        "s_held": [e["id"] for e in by_sha(sheld, "sheld-eval")
                   [:sizes["s_held"]]],
        "stated_guard": [e["id"] for e in by_sha(
            [x for x in train13 if x["family"] == 1], "stg")
            [:sizes["stated_guard"]]],
        "refusal_guard": [e["id"] for e in by_sha(
            [x for x in train13 if x["family"] == 3], "rfg")
            [:sizes["refusal_guard"]]],
    }

    out = args.out_dir or os.path.join(_ROOT, "data", "rules2-train")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "corpus.jsonl"), "w") as f:
        for e in examples:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    for name, obj in (("c1shuf-map.json",
                       {"seed": SEED_SHUF, "algorithm":
                        "FORCED FLIP of family-2 TRAIN targets to the "
                        "item's other 2-option decode candidate "
                        "(PROPOSED-ASM-1803, REWORK-3 entity form; "
                        "supersedes the rework-2 label-block rotation — no "
                        "cross-item label space exists for per-item NAME "
                        "targets; deterministic, seed retained for "
                        "provenance only) — shuffled_answer != "
                        "original_answer holds for EVERY item by "
                        "construction; ANTI-CORRELATED control, disclosed",
                        "assertion": "shuffled_answer != original_answer "
                                     "holds for all mapped items (fail-"
                                     "closed ERR_SHUFFLE otherwise)",
                        "disclosure": shuf_disclosure,
                        "map": shuf_map}),
                      ("b1-upsample.json",
                       {"rule": "cyclic repetition of sha-sorted stated+"
                                "refusal train ids to |B2| (ASM-1425/1447)",
                        "ids": upsample}),
                      ("eval-samples.json", eval_samples)):
        with open(os.path.join(out, name), "w") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
            f.write("\n")

    fam_counts = {}
    for e in examples:
        key = "family%d_%s_%s" % (e["family"], e["kind"], e["split"])
        fam_counts[key] = fam_counts.get(key, 0) + 1
    manifest = {
        "corpus": "rules2-train",
        "mode": "MOCK" if args.mock else "REAL",
        "design": "docs/next/design/rules-2-train-time.md SS2.1/2.2 as "
                  "amended by Appendix B (REWORK-3: rules-1-c ENTITY-form "
                  "re-render; PROPOSED-ASM-1800..)",
        "answer_form": "entity (rules-1-c / nsk1 g2b form 2): 'Who is the "
                       "<rel> of <base>?' -> object NAME; per-cell 2-option "
                       "anti-echo decode set in `options` (chance 0.5, "
                       "disclosed); typing cells keep the man/woman 2-option "
                       "form; refusal target appended at decode time",
        "entity_uniqueness_rule": "family-2 chain cells restrict context to "
                                  "the derivation's stated support (proof "
                                  "leaves + support gender facts + UNA; the "
                                  "3-name two-hop nsk1 item shape); the "
                                  "unique-answer property is asserted per "
                                  "cell in the restricted closure; "
                                  "ambiguous/non-3-name cells skipped WITH "
                                  "COUNTS (PROPOSED-ASM-1801)",
        "generator": "poc/rules-2/materialise_closure.py",
        "generator_sha256": sha256_file(os.path.abspath(__file__)),
        "engine": "poc/rules-1/twin_engine.py (PINNED, byte-exact, "
                  "PROPOSED-ASM-1437)",
        "pins_verified": pins,
        "seeds": {"synthetic_expansion": SEED_SYN, "c1shuf": SEED_SHUF},
        "c1p_label_derangement": shuf_disclosure,
        "n_syn_families": n_fam, "n_dev_families": n_dev,
        "n_examples": len(examples),
        "n_train_family2": len(train2), "n_train_family13": len(train13),
        "n_sheld": len(sheld),
        "sheld_rule": "sha256('sheld|'+id) fraction < %.2f over non-dev "
                      "family-2 cells (PROPOSED-ASM-1444)" % SHELD_FRAC,
        "family_kind_split_counts": dict(sorted(fam_counts.items())),
        "exclusion_ledger": counts,
        "name_disjointness": "asserted fail-closed vs nsk1-clutrr item "
                             "lexicons and nsk1-eval lexicon at TOKEN level "
                             "(PROPOSED-ASM-1442, rework-2 per cross-vendor "
                             "review item 5: full name OR any whitespace "
                             "token); world-v0 collisions excluded, counted "
                             "AND listed by component id",
        "refusal_answer": REFUSAL_ANSWER,
        "b3_note": "proof_sidecar is NEVER rendered into B2 training text; "
                   "B3 renders it before the answer (design SS2.2 family 4)",
    }
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    digest = corpus_kot_hash(out)
    print("rules2-train built (%s): %d examples (%d fam2-train, %d fam13-"
          "train, %d sheld) -> %s" % (manifest["mode"], len(examples),
                                      len(train2), len(train13), len(sheld),
                                      out))
    print("exclusion ledger: %s" % json.dumps(counts, sort_keys=True))
    print("kot-corpus-hash(rules2-train) = %s" % digest)
    return digest


# ---------------------------------------------------------------------------
# c8 — the train-bytes projection gate (PROPOSED-ASM-1427 / 1445)
# ---------------------------------------------------------------------------
def query_pair_item(item):
    """(a, b) URNs of a nsk1-clutrr item's eval query — SEMANTICS VERBATIM
    from poc/rules-1/rules1_runner.py query_pair (duplicated so the $0 CPU
    gate does not import the GPU-runner module tree; REWORK-3)."""
    if item["hop1"]:
        a = item["hop1"]["subject"]
        b = [u for u in item["lexicon"]
             if u not in (a, item["hop1_bridge"])][0]
        return a, b
    q = item["question"]
    name_a, name_b = q[len("How is "):-1].split(" related to ")
    n2u = {v: k for k, v in item["lexicon"].items()}
    return n2u[name_a], n2u[name_b]


def c8(args):
    pins = verify_pins()
    corpus_dir = args.out_dir or os.path.join(_ROOT, "data", "rules2-train")
    examples = [json.loads(x) for x in
                open(os.path.join(corpus_dir, "corpus.jsonl"))]
    eval_samples = json.load(open(os.path.join(corpus_dir,
                                               "eval-samples.json")))
    byid = {e["id"]: e for e in examples}
    train = [e for e in examples if e["split"] == "train"]

    # GS-family FLAT lookup over the B2 TRAINING BYTES — no joins, no
    # inference (DECONF-A1 GS lineage; certificate.py projection_answer).
    # REWORK-3 (entity form):
    #   (i)  QA index: trained (base-name, rel-word) entity question ->
    #        trained NAME answer (typing questions keyed verbatim)
    #   (ii) aligned fact-line index: parsed "O is S's w." -> (S, w) -> O
    #        (entity-directional: base+relation-word -> object NAME)
    qa, factline = {}, {}

    def ent_key(q):
        # 'Who is the <rel> of <base>?' -> (base, rel); None otherwise
        if q.startswith("Who is the ") and " of " in q and q.endswith("?"):
            rel, base = q[len("Who is the "):-1].split(" of ", 1)
            return (base, rel)
        return None

    for e in train:
        k = ent_key(e["question"])
        if k is not None:
            qa.setdefault(k, set()).add(e["answer"])
        else:
            qa.setdefault((e["question"], "#typing"), set()).add(e["answer"])
        for line in e["context"]:
            if " is " in line and "'s " in line and line.endswith("."):
                left, right = line[:-1].split(" is ", 1)
                if "'s " in right:
                    subj, word = right.rsplit("'s ", 1)
                    factline.setdefault((subj, word), set()).add(left)

    def project(base, rel):
        hits = qa.get((base, rel))
        if not hits:
            hits = factline.get((base, rel))
        if not hits:
            return None
        return sorted(hits)[0] if len(hits) == 1 else "AMBIG"

    def score_ids(ids):
        n = rec = corr = 0
        by_kind = {}
        for iid in ids:
            e = byid[iid]
            k = ent_key(e["question"])
            if k is not None:
                p = project(*k)
            else:
                hits = qa.get((e["question"], "#typing"))
                p = (sorted(hits)[0] if hits and len(hits) == 1
                     else ("AMBIG" if hits else None))
            n += 1
            kk = by_kind.setdefault(e["kind"], {"n": 0,
                                                "recovered_correct": 0})
            kk["n"] += 1
            if p not in (None, "AMBIG"):
                rec += 1
                hit = int(p == e["answer"])
                corr += hit
                kk["recovered_correct"] += hit
        return {"n": n, "recovered": rec, "recovered_correct": corr,
                "recovered_acc": corr / n if n else None,
                "by_kind": dict(sorted(by_kind.items())),
                "disclosure": "cover (E1) cells share their (base, rel) "
                              "entity key with trained family-1 stated "
                              "cells of the same component, so they ARE "
                              "flat-lookup-recoverable; chain cells whose "
                              "(base, rel) key is AMBIGUOUS across support "
                              "contexts (two grandmothers) are NOT "
                              "lookup-recoverable — the s_mem projection "
                              "anchor is therefore <1.0 on the entity form "
                              "and stratified by kind (REWORK-3 "
                              "re-derivation of the PROPOSED-ASM-1444 "
                              "disclosure)"}

    # S-out: the 858 covered nsk1-clutrr items on the ENTITY question
    # ('Who is the <gold_rel> of <base>?' -> chain-top NAME) — the rules-1-c
    # eval form, reconstructed here exactly as rules1_runner.build_context
    # renders it (query_pair semantics duplicated above).
    items = [json.loads(x) for x in
             open(os.path.join(_ROOT, "data", "nsk1-clutrr", "items.jsonl"))]
    covered = [i for i in items if i["stratum"] == "covered"]
    if args.mock:
        covered = covered[:MOCK["n_sout"]]
    sout_n = sout_rec = sout_corr = 0
    first_opt_hits = 0
    for it in covered:
        a, b = query_pair_item(it)
        names = it["lexicon"]
        base, gold_name = names[a], names[b]
        rel = it["gold_relation"]
        p = project(base, rel)
        sout_n += 1
        opts = sorted(s for u, s in names.items() if u != a)
        first_opt_hits += int(gold_name == opts[0])
        if p not in (None, "AMBIG"):
            sout_rec += 1
            sout_corr += int(p == gold_name)
    sout_acc = sout_corr / sout_n if sout_n else None
    gate_pass = sout_acc is not None and sout_acc <= C8_SOUT_CEILING

    first_opt_floor = first_opt_hits / sout_n if sout_n else None
    result = {
        "c8": "rules-2 train-bytes projection (PROPOSED-ASM-1427; REWORK-3 "
              "entity form, PROPOSED-ASM-1804)",
        "mode": "MOCK" if args.mock else "REAL",
        "status": "instrument gate artifact; NO feasibility conclusion is "
                  "stated here — verdicts belong to the pinned analysis + "
                  "verdict-gen",
        "construction": "GS-family flat lookup over the PINNED B2 training "
                        "bytes: QA index (trained (base, rel) entity "
                        "question -> NAME) + aligned fact-line index "
                        "((base-name, relation-word) -> object NAME); NO "
                        "joins, NO inference (DECONF-A1 GS lineage, "
                        "certificate.projection_answer analog). REWORK-3 "
                        "ceiling re-argument at chance 0.5: the gate metric "
                        "is recovered-correct/n, and eval surface names are "
                        "TOKEN-disjoint from training names (fail-closed "
                        "guard), so a lookup cannot even emit an in-lexicon "
                        "eval NAME — recovery is 0 by construction and the "
                        "0.10 ceiling is conservative INDEPENDENT of the "
                        "decode chance floor (0.5 here vs 1/24 before): the "
                        "ceiling bounds lookup leakage, not guessing",
        "gate": {"stratum": "S-out (covered nsk1-clutrr, entity form, vs "
                            "third-party gold chain-top NAME)",
                 "n": sout_n, "recovered": sout_rec,
                 "recovered_correct": sout_corr,
                 "sout_recovered_acc": sout_acc,
                 "ceiling": C8_SOUT_CEILING, "gate_pass": bool(gate_pass)},
        "descriptives": {
            "s_mem_projection": score_ids(eval_samples["s_mem"]),
            "s_held_projection": score_ids(eval_samples["s_held"]),
            "c4_trivial_floors_sout": {
                "abstain_all_acc": 0.0,
                "random_two_option_acc": 0.5,
                "always_first_option_acc": first_opt_floor,
                "note": "REWORK-3 floors at the 2-option entity surface "
                        "(chance 0.5 DISCLOSED; the 23-word majority floor "
                        "is form-inapplicable): abstain-all 0.0; random "
                        "0.5; the measured sorted-first-option incidence "
                        "brackets position bias. The 'pick the non-bridge "
                        "name' structural shortcut (gold = chain-top by "
                        "construction on 2-hop items) is NOT a train-bytes "
                        "lookup and is OUT OF SCOPE for this gate — it is "
                        "the registered DESIGN-OPEN PROPOSED-ASM-1806 for "
                        "the pre-freeze review. The primary is a paired "
                        "B2-B0 lift, not an absolute accuracy"},
        },
        "pins_verified": pins,
        "corpus_kot_hash_rules2_train": corpus_kot_hash(corpus_dir),
        "train_index_sizes": {"qa_pairs": len(qa),
                              "fact_line_pairs": len(factline),
                              "train_examples": len(train)},
    }
    out_dir = (args.out_dir if args.mock
               else os.path.join(_HERE, "results"))
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "c8-result%s.json"
                       % ("-mock" if args.mock else ""))
    with open(out, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"gate": result["gate"],
                      "s_mem": result["descriptives"]["s_mem_projection"],
                      "s_held": result["descriptives"]["s_held_projection"]},
                     indent=1))
    print("->", out)
    if not gate_pass:
        raise SystemExit("ERR_C8_GATE: S-out recovered acc %.4f > ceiling "
                         "%.2f — split broken, INSTRUMENT-INVALID, no GPU "
                         "spend" % (sout_acc, C8_SOUT_CEILING))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "c8"])
    ap.add_argument("--mock", action="store_true",
                    help="tiny corpus, $0, labelled MOCK; requires --out-dir")
    ap.add_argument("--out-dir", default=None,
                    help="override output dir (REQUIRED with --mock; default "
                         "data/rules2-train)")
    args = ap.parse_args()
    if args.mock and not args.out_dir:
        raise SystemExit("ERR_ARGS: --mock requires --out-dir (never "
                         "overwrites data/rules2-train)")
    if args.cmd == "build":
        build(args)
    else:
        c8(args)


if __name__ == "__main__":
    main()
