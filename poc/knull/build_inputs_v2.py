#!/usr/bin/env python3
"""knull-v2 — input builder for the SUPERSEDING K-NULL record (knull-v2).

V2 DELTA (the ONLY changes from the pinned v1 builder poc/knull/
build_inputs.py, sha256 in the frozen knull record; the g3-llmproxy-v2
custody pattern — changed artifacts carry fresh v2 paths, the frozen v1
inputs under poc/knull/inputs/ stay byte-untouched):
  - reads the RE-AUTHORED plain store poc/knull/inputs-v2/plain-authored.json
    (maintainer's lexicographic standard; ratified ASM-0703 quality gate);
  - writes every output under poc/knull/inputs-v2/ (stores/, items/,
    manifest.json, plain-spotcheck.json);
  - VERSION 2.0.0, GENERATED 2026-07-11.
GEN_SEED, skeleton schedule, leak checks, pairing, opaque/kernel store
logic and all rendering are byte-carried from v1 — the arms and the
cross-arm pairing contract are unchanged; only the plain arm's authored
bytes (and whatever item type mix follows from them via the joint
substitution ladder) differ. Original v1 docstring follows.

knull — input builder for the K-NULL content-injection ablation (DRAFT).

Design doc: docs/design-knull-content-injection-ablation.md (the content-
injection map in that doc is the normative statement of WHY these arms are
built this way). Registry line id: knull-content-injection-ablation.

Builds, deterministically (generator seed KNULL GEN_SEED, no wall-clock):

  stores/plain/<label>.json    aligned CONVENTIONAL store — plain typed schema,
                               same record<->item alignment, ZERO NSM content.
                               Definitions are the AUTHORED plain-dictionary
                               set (inputs/plain-authored.json, fork F-KN-A
                               option (ii), disclosure in that file), linted
                               fail-closed by lint_plain_store.py at build
                               (pre-freeze gate G-1). plain_store_placeholder
                               is FALSE in the manifest (gate G-2).
  stores/opaque/<label>.json   opaque-ID store — semantically empty nonce
                               definitions, alignment preserved, REAL logic
                               (no authoring needed). Word target is TOKEN-
                               calibrated: nonce syllable text tokenizes at
                               ~2.09x the rate of NSM English under the pinned
                               SmolLM2 tokenizer (G-3 re-check artifact
                               inputs/g3-token-band.json), so the word target
                               is scaled by OPAQUE_TOKEN_CALIB to keep the
                               per-query FLOPs budget matched (the +/-20%
                               parity gate).
  items/kernel.jsonl           per-arm item sets rendered from ONE shared
  items/plain.jsonl            skeleton per (concept, slot): same concept, same
  items/opaque.jsonl           template type, same distractor/donor concept
                               coordinates, same option-slot ordering — arms
                               differ ONLY where store bytes are injected
                               (map points I-1/I-2/I-3 in the design doc).
  manifest.json                sha256 pins for every store file + item file +
                               upstream provenance pins.

The kernel arm's store is the EXISTING pinned record set (data/kernel-v0 +
data/molecules-v0); no kernel bytes are copied or modified.

Leak checks carried over from data/d-qa-r/build-dqar.py (helpers copied
VERBATIM with attribution; that file is another line's frozen input and is
not imported to avoid coupling to its module-level build): LC1 label-in-gloss,
LC3 false-claim non-entailment, LC4 duplicate option text, LC8 prompt-surface
disjointness of the KERNEL arm vs all 650 d-qa + 1000 d-qa-r logged surfaces.
Joint substitution: if a check fails for ANY arm, the skeleton advances for
ALL arms, so the cross-arm pairing (skeleton_uid) is never broken.

FAIL-CLOSED: any violation aborts with KNULL_ERR_*; nothing is written.

Usage: python3 poc/knull/build_inputs.py     ($0, CPU-only, deterministic)
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SCHEMA = "kot-knull-inputs/1"
VERSION = "2.0.0"
GENERATED = "2026-07-11"                    # fixed build date, never wall-clock
GEN_SEED = "knull/1|knull-content-injection-ablation|20260710"
SLOTS_PER_CONCEPT = 10                      # 108 concepts x 10 = 1080 skeletons
N_ITEMS = 1000                              # rank-prefix consumed by the runner
MIN_SEGMENT_CHARS = 15                      # = build-dqa.py contract
FALSE_CLAIM_JACCARD_MAX = 0.5
WORDBAND_FRAC = 0.25                        # gloss word-count band vs reference
# Opaque word-target calibration (G-3): nonce syllable words tokenize at
# ~2.9 tokens/word vs ~1.4 tokens/word for the NSM glosses under the pinned
# SmolLM2-135M-Instruct tokenizer (revision 12fd25f7..., tokenizer.json sha256
# 9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fcd888e47c) — an
# uncalibrated word-count band left the opaque store at 2.09x kernel tokens
# (measured; inputs/g3-token-band.json). The opaque word target is therefore
# NSM-word-count * OPAQUE_TOKEN_CALIB so the TOKEN budget — the FLOPs-parity
# quantity the +/-20% gate meters — stays matched. Verified post-build by
# poc/knull/check_token_band.py (gate G-3).
OPAQUE_TOKEN_CALIB = 0.48
ARMS = ("kernel", "plain", "opaque")
TYPE_CYCLE = ("def-match", "term-match", "claim-true", "claim-false")
PLAIN_AUTHORED = "plain-authored.json"      # inputs/, fork F-KN-A option (ii)


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


# --- deterministic hash helpers (VERBATIM shape from data/d-qa-r/build-dqar.py,
# --- re-salted with the knull GEN_SEED) --------------------------------------

def h(s):
    return int.from_bytes(
        hashlib.sha256(("%s|%s" % (GEN_SEED, s)).encode("utf-8")).digest(), "big")


def hhex(s):
    return hashlib.sha256(("%s|%s" % (GEN_SEED, s)).encode("utf-8")).hexdigest()


def qhash(question, options):
    """UNSALTED prompt-surface hash — byte-identical construction to
    build-dqar.py::qhash so LC8 is comparable across d-qa / d-qa-r / knull."""
    blob = question + "||" + "|".join(o["text"] for o in (options or []))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def pick_k(seed, n, k, exclude=frozenset()):
    out = []
    i = 0
    while len(out) < k:
        idx = h("%s|%d" % (seed, i)) % n
        i += 1
        if idx in exclude or idx in out:
            if i > 10000:
                die("KNULL_ERR_PICK", "cannot draw %d distinct (seed %s)" % (k, seed))
            continue
        out.append(idx)
    return out


TOKEN_RE = re.compile(r"[a-z]+")
URN_MARKUP_RE = re.compile(r"\{urn:[^|}]+\|([^}]*)\}")


def tokens(text):
    return set(TOKEN_RE.findall(text.lower()))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def word_in(word, text):
    return re.search(r"\b%s\b" % re.escape(word.lower()), text.lower()) is not None


def render_plain(text):
    """VERBATIM canonical-record rendering (build-dqa.py / f2b_runner.py)."""
    text = URN_MARKUP_RE.sub(r"\1", text)
    text = text.replace(" [m]", "").replace("[m]", "")
    return re.sub(r"  +", " ", text).strip()


def segments(gloss):
    """VERBATIM claim segmentation (build-dqa.py / f2b_runner.py)."""
    out = []
    for seg in re.split(r"[.;]", gloss):
        seg = seg.strip()
        if len(seg) >= MIN_SEGMENT_CHARS and '"' not in seg and seg not in out:
            out.append(seg)
    return out


# --------------------------------------------------------------- load sources

def load_covered():
    """The 108 covered concepts — identical loader semantics to build-dqar.py."""
    concepts = []
    kdir = os.path.join(ROOT, "data", "kernel-v0", "concepts")
    for name in sorted(os.listdir(kdir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(kdir, name)
        rec = json.load(open(path, encoding="utf-8"))
        concepts.append({
            "label": rec["label"], "urn": rec["id"], "gloss": rec["gloss"].strip(),
            "source": "kernel-v0",
            "record_path": "data/kernel-v0/concepts/" + name,
            "record_sha256": file_sha256(path),
        })
    mdir = os.path.join(ROOT, "data", "molecules-v0", "molecules")
    for name in sorted(os.listdir(mdir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(mdir, name)
        rec = json.load(open(path, encoding="utf-8"))
        concepts.append({
            "label": rec["label"], "urn": rec["id"],
            "gloss": render_plain(rec["groundingNote"]),
            "source": "molecules-v0",
            "record_path": "data/molecules-v0/molecules/" + name,
            "record_sha256": file_sha256(path),
        })
    if len(concepts) != 108:
        die("KNULL_ERR_SOURCE", "expected 108 covered concepts, got %d" % len(concepts))
    labels = [c["label"] for c in concepts]
    if len(set(labels)) != len(labels):
        die("KNULL_ERR_SOURCE", "duplicate covered labels")
    return concepts


def load_logged_prompt_hashes():
    """LC8 reference: every logged d-qa (650) + d-qa-r (1000) prompt surface."""
    taken = set()
    n = 0
    for rel in (("d-qa", "covered.jsonl"), ("d-qa", "control.jsonl"),
                ("d-qa-r", "covered.jsonl")):
        path = os.path.join(ROOT, "data", rel[0], "items", rel[1])
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                it = json.loads(line)
                taken.add(qhash(it["question"], it["options"]))
                n += 1
    if n != 1650:
        die("KNULL_ERR_SOURCE", "expected 650+1000 logged reference items, got %d" % n)
    return taken


# ----------------------------------------------------- store text generators

SYLLABLES = ["ba", "de", "fi", "go", "hu", "ka", "le", "mi",
             "no", "pu", "ra", "se", "ti", "vo", "wu", "za"]

def nonce_word(key):
    n = 2 + h("%s|len" % key) % 2
    return "".join(SYLLABLES[h("%s|syl|%d" % (key, i)) % len(SYLLABLES)]
                   for i in range(n))


def word_count(text):
    return len(text.split())


def opaque_target_words(concept):
    """TOKEN-calibrated opaque word target (see the OPAQUE_TOKEN_CALIB
    derivation note at the top of this file; gate G-3)."""
    return max(6, int(round(word_count(concept["gloss"]) * OPAQUE_TOKEN_CALIB)))


def opaque_gloss(concept):
    """Semantically empty nonce definition: >=2 segments (so claim items
    exist), word target TOKEN-calibrated to the NSM gloss so the per-query
    FLOPs budget stays matched under the pinned tokenizer (gate G-3;
    verified post-build by check_token_band.py). REAL arm content (no
    authoring gate)."""
    nsm = concept["gloss"]
    target = opaque_target_words(concept)
    n_seg = max(2, min(len(segments(nsm)), target // 3))
    per_seg = max(2, target // n_seg)
    segs = []
    for si in range(n_seg):
        words = [nonce_word("%s|op|%d|%d" % (concept["label"], si, wi))
                 for wi in range(per_seg)]
        seg = " ".join(words)
        while len(seg) < MIN_SEGMENT_CHARS:      # contract: segmentable claims
            seg += " " + nonce_word("%s|pad|%d|%d" % (concept["label"], si, len(seg)))
        segs.append(seg)
    return "; ".join(segs)


def load_plain_authored(concepts):
    """The AUTHORED plain-dictionary store (fork F-KN-A option (ii),
    disclosure inside the file) — linted fail-closed via lint_plain_store
    (gate G-1) before any item is rendered from it. Returns
    (definitions, manifest_block)."""
    path = os.path.join(HERE, "inputs-v2", PLAIN_AUTHORED)
    with open(path, encoding="utf-8") as f:
        authored = json.load(f)
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import lint_plain_store
    findings = []
    lint_plain_store.lint(authored, concepts, findings)
    if findings:
        for code, msg in findings[:20]:
            sys.stderr.write("%s: %s\n" % (code, msg))
        die("KNULL_ERR_PLAIN_LINT",
            "authored plain store failed lint_plain_store (%d finding(s))"
            % len(findings))
    block = {
        "path": "poc/knull/inputs-v2/%s" % PLAIN_AUTHORED,
        "sha256": file_sha256(path),
        "authoring_disclosure": authored["authoring_disclosure"],
        "lint": "poc/knull/lint_plain_store.py PASS (checks D-1, L-1..L-5, "
                "R-1..R-4) - re-run fail-closed at this build",
    }
    return authored["definitions"], block


# ------------------------------------------------------------- store assembly

def build_stores(concepts):
    all_labels = [c["label"] for c in concepts]
    stores = {"kernel": {}, "plain": {}, "opaque": {}}
    for c in concepts:
        stores["kernel"][c["label"]] = {
            "urn": c["urn"], "gloss": c["gloss"],
            "record_path": c["record_path"], "record_sha256": c["record_sha256"],
            "records_root": "REPO_ROOT",
        }
    plain_defs, authored_block = load_plain_authored(concepts)
    stores["_plain_authored_block"] = authored_block
    seen = {"plain": set(), "opaque": set()}
    for arm, gen, ref_words in (
            # plain: word band vs the NSM gloss (English-vs-English, the
            # measured token ratio is ~0.90 — inputs/g3-token-band.json)
            ("plain", lambda c: plain_defs[c["label"]],
             lambda c: word_count(c["gloss"])),
            # opaque: word band vs the TOKEN-calibrated target (G-3)
            ("opaque", opaque_gloss, opaque_target_words)):
        adir = os.path.join(HERE, "inputs-v2", "stores", arm)
        os.makedirs(adir, exist_ok=True)
        for c in concepts:
            gl = gen(c)
            if gl in seen[arm]:
                die("KNULL_ERR_DUPGLOSS", "%s store: duplicate gloss (%s)"
                    % (arm, c["label"]))
            seen[arm].add(gl)
            if word_in(c["label"], gl):
                die("KNULL_ERR_LC1", "%s/%s: own label in gloss" % (arm, c["label"]))
            wc, wn = ref_words(c), word_count(gl)
            if not (wc * (1 - WORDBAND_FRAC) <= wn <= max(
                    wc * (1 + WORDBAND_FRAC), wc + 8)):
                die("KNULL_ERR_WORDBAND", "%s/%s: %d words vs reference %d (band %.0f%%)"
                    % (arm, c["label"], wn, wc, WORDBAND_FRAC * 100))
            if len(segments(gl)) < 2:
                die("KNULL_ERR_SEGMENTS", "%s/%s: <2 admissible claim segments"
                    % (arm, c["label"]))
            rec = {"id": "urn:knull-%s:%s" % (arm, c["label"]),
                   "label": c["label"],
                   "schema": "kot-knull-store/1",
                   "store": arm,
                   "aligned_to": c["urn"],
                   "gloss": gl}
            path = os.path.join(adir, "%s.json" % c["label"])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(rec, f, indent=1, sort_keys=True)
                f.write("\n")
            stores[arm][c["label"]] = {
                "urn": rec["id"], "gloss": gl,
                "record_path": "%s.json" % c["label"],
                "record_sha256": file_sha256(path),
                "records_root": "poc/knull/inputs-v2/stores/%s" % arm,
            }
    return stores


# ------------------------------------------------------------- item rendering

def option_order(sid, v, sources):
    """Shared-coordinate option shuffle: sort by hash of the option's SOURCE
    concept urn (not its text), so all arms get the IDENTICAL A-D layout."""
    keyed = sorted(sources, key=lambda s: hhex("%s|v%d|opt|%s" % (sid, v, s[0])))
    return keyed


def build_items(concepts, stores, taken_logged, checks):
    n = len(concepts)
    labels = [c["label"] for c in concepts]
    items = {a: [] for a in ARMS}
    taken = {a: set(taken_logged) if a == "kernel" else set(taken_logged)
             for a in ARMS}   # LC8 vs logged surfaces enforced for EVERY arm
    for slot in range(1, SLOTS_PER_CONCEPT + 1):
        for ci, c in enumerate(concepts):
            sid = "knull:%s:s%d" % (c["label"], slot)
            typ = TYPE_CYCLE[(slot - 1) % len(TYPE_CYCLE)]
            built = try_build(sid, typ, ci, c, concepts, stores, labels,
                              taken, checks)
            if built is None:
                die("KNULL_ERR_BUILD", "no admissible item for %s (%s)" % (sid, typ))
            typ_used, per_arm = built
            if typ_used != typ:
                checks["substitutions"].append({"sid": sid, "from": typ,
                                                "to": typ_used})
            for a in ARMS:
                it = per_arm[a]
                st = stores[a][c["label"]]
                items[a].append({
                    "id": "knull:%s:%s:s%d" % (a, c["label"], slot),
                    "skeleton_uid": sid, "slot": slot,
                    "label": c["label"], "urn": st["urn"],
                    "type": it["type"], "question": it["question"],
                    "options": it["options"], "answer": it["answer"],
                    **({"claim": it["claim"]} if "claim" in it else {}),
                    **({"claim_source": it["claim_source"]}
                       if "claim_source" in it else {}),
                    "kernel_checkable": True,
                    "record_path": st["record_path"],
                    "record_sha256": st["record_sha256"],
                    "store": a, "source": c["source"],
                })
                taken[a].add(qhash(it["question"], it["options"]))
    # deterministic rank over skeletons (shared across arms — pairing key)
    sk_rank = {}
    for a in ARMS:
        for it in items[a]:
            sk_rank.setdefault(it["skeleton_uid"],
                               h("rank|%s" % it["skeleton_uid"]))
    order = sorted(sk_rank, key=lambda s: (sk_rank[s], s))
    rank_of = {s: i for i, s in enumerate(order)}
    for a in ARMS:
        for it in items[a]:
            it["rank"] = rank_of[it["skeleton_uid"]]
        items[a].sort(key=lambda x: x["rank"])
    return items


def try_build(sid, typ, ci, c, concepts, stores, labels, taken, checks):
    """Render one skeleton in ALL arms; None on structural failure. Joint
    substitution ladder: term-match -> def-match; claim-true -> claim-false."""
    if typ == "term-match":
        r = render_term_match(sid, ci, c, concepts, stores, labels, taken, checks)
        if r is not None:
            return ("term-match", r)
        checks["lc1_substituted"] += 1
        typ = "def-match"
    if typ == "def-match":
        r = render_def_match(sid, ci, c, concepts, stores, taken, checks)
        return ("def-match", r) if r is not None else None
    if typ == "claim-true":
        r = render_claim_true(sid, c, stores, taken, checks)
        if r is not None:
            return ("claim-true", r)
        typ = "claim-false"
    if typ == "claim-false":
        r = render_claim_false(sid, ci, c, concepts, stores, taken, checks)
        return ("claim-false", r) if r is not None else None
    die("KNULL_ERR_TYPE", typ)


def render_def_match(sid, ci, c, concepts, stores, taken, checks):
    n = len(concepts)
    q = 'Which option gives the meaning of the word "%s"?' % c["label"]
    for v in range(32):
        dis = pick_k("%s|dis|v%d" % (sid, v), n, 3, exclude={ci})
        srcs = [(c["label"], True)] + [(concepts[i]["label"], False) for i in dis]
        ordered = option_order(sid, v, [(s[0], s[1]) for s in srcs])
        per_arm, ok = {}, True
        for a in ARMS:
            opts, ans = [], None
            for i, (src_label, is_ans) in enumerate(ordered):
                text = stores[a][src_label]["gloss"]
                opts.append({"key": "ABCD"[i], "text": text})
                if is_ans:
                    ans = "ABCD"[i]
            texts = [o["text"] for o in opts]
            if len(set(texts)) != 4:
                ok = False           # LC4 duplicate option text in this arm
                break
            if qhash(q, opts) in taken[a]:
                checks["lc8_retries"] += 1
                ok = False
                break
            per_arm[a] = {"type": "def-match", "question": q,
                          "options": opts, "answer": ans}
        if ok:
            checks["lc4_option_sets"] += 1
            return per_arm
    return None


def render_term_match(sid, ci, c, concepts, stores, labels, taken, checks):
    # LC1 in ANY arm -> joint substitution (caller falls back to def-match)
    for a in ARMS:
        if word_in(c["label"], stores[a][c["label"]]["gloss"]):
            return None
    checks["lc1_checked"] += 1
    n = len(concepts)
    for v in range(32):
        dis = pick_k("%s|labels|v%d" % (sid, v), n, 3, exclude={ci})
        srcs = [(c["label"], True)] + [(concepts[i]["label"], False) for i in dis]
        ordered = option_order(sid, v, srcs)
        opts = [{"key": "ABCD"[i], "text": lab} for i, (lab, _) in enumerate(ordered)]
        ans = "ABCD"[[s[1] for s in ordered].index(True)]
        per_arm, ok = {}, True
        for a in ARMS:
            q = 'A word whose definition is: "%s". Which word is it?' \
                % stores[a][c["label"]]["gloss"]
            if qhash(q, opts) in taken[a]:
                checks["lc8_retries"] += 1
                ok = False
                break
            per_arm[a] = {"type": "term-match", "question": q,
                          "options": opts, "answer": ans}
        if ok:
            return per_arm
    return None


def claim_question(label, claim):
    return ('According to the definition of "%s", is the following true of %s? '
            '"%s" Answer yes or no.' % (label, label, claim))


def render_claim_true(sid, c, stores, taken, checks):
    per_arm = {}
    for a in ARMS:
        segs = segments(stores[a][c["label"]]["gloss"])
        if not segs:
            return None            # structural: joint substitution
        start = h("%s|segstart|%s" % (sid, a)) % len(segs)
        got = None
        for j in range(len(segs)):
            claim = segs[(start + j) % len(segs)]
            q = claim_question(c["label"], claim)
            if qhash(q, None) in taken[a]:
                checks["lc8_retries"] += 1
                continue
            got = {"type": "claim-true", "question": q, "options": None,
                   "answer": "yes", "claim": claim}
            break
        if got is None:
            return None
        per_arm[a] = got
    checks["lc6_true_claims"] += 1
    return per_arm


def render_claim_false(sid, ci, c, concepts, stores, taken, checks):
    n = len(concepts)
    for t in range(512):
        di = h("%s|donor|%d" % (sid, t)) % n
        donor = concepts[di]
        if donor["label"] == c["label"]:
            continue
        per_arm, ok = {}, True
        for a in ARMS:
            own = stores[a][c["label"]]["gloss"]
            dgl = stores[a][donor["label"]]["gloss"]
            if dgl == own:
                ok = False
                break
            dsegs = segments(dgl)
            if not dsegs:
                ok = False
                break
            claim = dsegs[h("%s|dseg|%d|%s" % (sid, t, a)) % len(dsegs)]
            if claim.lower() in own.lower() \
               or jaccard(tokens(claim), tokens(own)) >= FALSE_CLAIM_JACCARD_MAX:
                checks["lc3_rejected"] += 1
                ok = False
                break
            q = claim_question(c["label"], claim)
            if qhash(q, None) in taken[a]:
                checks["lc8_retries"] += 1
                ok = False
                break
            per_arm[a] = {"type": "claim-false", "question": q, "options": None,
                          "answer": "no", "claim": claim,
                          "claim_source": donor["label"]}
        if ok:
            checks["lc3_accepted"] += 1
            return per_arm
    return None


# ---------------------------------------------------------------------- main

def main():
    os.makedirs(os.path.join(HERE, "inputs-v2", "items"), exist_ok=True)
    concepts = load_covered()
    taken_logged = load_logged_prompt_hashes()
    checks = {"lc1_checked": 0, "lc1_substituted": 0, "lc3_accepted": 0,
              "lc3_rejected": 0, "lc4_option_sets": 0, "lc6_true_claims": 0,
              "lc8_retries": 0, "substitutions": []}
    stores = build_stores(concepts)
    authored_block = stores.pop("_plain_authored_block")
    items = build_items(concepts, stores, taken_logged, checks)

    pins = {}
    for a in ARMS:
        path = os.path.join(HERE, "inputs-v2", "items", "%s.jsonl" % a)
        with open(path, "w", encoding="utf-8") as f:
            for it in items[a]:
                f.write(json.dumps(it, sort_keys=True,
                                   separators=(",", ":")) + "\n")
        pins["items_%s_sha256" % a] = file_sha256(path)
    for a in ("plain", "opaque"):
        adir = os.path.join(HERE, "inputs-v2", "stores", a)
        pins["store_%s" % a] = {
            name: file_sha256(os.path.join(adir, name))
            for name in sorted(os.listdir(adir)) if name.endswith(".json")}

    # cross-arm pairing invariant: identical skeleton_uid sequences
    seqs = [tuple(it["skeleton_uid"] for it in items[a]) for a in ARMS]
    if not (seqs[0] == seqs[1] == seqs[2]):
        die("KNULL_ERR_PAIRING", "skeleton sequences differ across arms")

    manifest = {
        "schema": SCHEMA, "version": VERSION, "generated": GENERATED,
        "generator_seed": GEN_SEED,
        "design_doc": "docs/design-knull-content-injection-ablation.md",
        "n_skeletons": len(seqs[0]), "n_items_planned_per_arm": N_ITEMS,
        "arms": list(ARMS),
        "plain_store_placeholder": False,
        "plain_store_note": ("AUTHORED plain-dictionary definitions (fork "
                             "F-KN-A option (ii)); source, disclosure and "
                             "lint state in plain_store_authored; gate G-1 "
                             "linted fail-closed at this build."),
        "plain_store_authored": authored_block,
        "opaque_token_calibration": {
            "factor": OPAQUE_TOKEN_CALIB,
            "why": ("nonce syllable words tokenize at ~2.09x NSM English "
                    "under the pinned SmolLM2 tokenizer; the opaque word "
                    "target is scaled so the TOKEN budget (the FLOPs-parity "
                    "gate quantity) stays matched; measured artifact "
                    "poc/knull/inputs-v2/g3-token-band.json (gate G-3)")},
        "kernel_store": "existing pinned records (data/kernel-v0 + "
                        "data/molecules-v0); records_root = repo root",
        "leak_checks": {k: v for k, v in checks.items() if k != "substitutions"},
        "substitutions_n": len(checks["substitutions"]),
        "substitutions": checks["substitutions"][:50],
        "provenance_pins": {
            "f2b_runner_py_sha256": file_sha256(
                os.path.join(ROOT, "poc", "f2b", "runner", "f2b_runner.py")),
            "f2b_manifest_sha256": file_sha256(
                os.path.join(ROOT, "poc", "f2b", "inputs", "f2b-manifest.json")),
            "build_dqar_py_sha256": file_sha256(
                os.path.join(ROOT, "data", "d-qa-r", "build-dqar.py")),
        },
        "pins": pins,
    }
    mpath = os.path.join(HERE, "inputs-v2", "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")

    # 10-item blind style spot-check for the maintainer (fork F-KN-A gate):
    # deterministic sample; judge reads items BEFORE the answer key.
    labels = [c["label"] for c in concepts]
    picks = pick_k("plain-spotcheck", len(labels), 10)
    spot = {
        "schema": "kot-knull-spotcheck/1",
        "instructions": ("BLIND style spot-check (fork F-KN-A, design doc "
                         "section 2.3): read the 10 definitions below "
                         "WITHOUT looking at answer_key. For each, judge: "
                         "(a) does it read as ordinary dictionary-register "
                         "English (not NSM-style controlled language)? "
                         "(b) is it a fair definition a general dictionary "
                         "could print? Record verdicts, then unblind."),
        "items": [{"id": i, "definition":
                   stores["plain"][labels[p]]["gloss"]}
                  for i, p in enumerate(picks)],
        "answer_key": {str(i): labels[p] for i, p in enumerate(picks)},
    }
    spath = os.path.join(HERE, "inputs-v2", "plain-spotcheck.json")
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(spot, f, indent=1, sort_keys=True)
        f.write("\n")

    print("knull inputs built: %d skeletons x %d arms; manifest %s"
          % (len(seqs[0]), len(ARMS), mpath))
    print("manifest sha256: %s" % file_sha256(mpath))


if __name__ == "__main__":
    main()
