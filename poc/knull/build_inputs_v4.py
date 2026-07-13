#!/usr/bin/env python3
"""knull-v2 Option-B — FOUR-ARM input builder for the accepted v4 plain store
(pre-freeze blocker B-1 of poc/knull/freeze-prep/README.md; implementation
spec docs/next/design/knull-optionb-analysis.md section 5, adapted v3->v4 per
poc/knull/freeze-prep/record-delta-v4.md).

V4 DELTA (the ONLY changes from the pinned v2 builder poc/knull/
build_inputs_v2.py; custody pattern — the pinned v1/v2 builders and the
frozen inputs under poc/knull/inputs/ + inputs-v2/ stay byte-untouched):

  - reads the ACCEPTED v4 plain store poc/knull/inputs-v4/plain-authored.json
    v4.0.0 (maintainer issue-17 acceptance + blind style sign-off 10/10,
    poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md), pinned fail-closed
    by sha256 (KNULL_ERR_STORE_PIN) and gated by the Option-B relaxed G-1
    contract lint_plain_store_v4.py run fail-closed at build
    (KNULL_ERR_PLAIN_LINT; ASM-1080);
  - adds the PLAIN-PADDED store (ASM-1082): the SAME concise v4 definition,
    deterministically padded back into the kernel-gloss word band
    [0.75*wc, max(1.25*wc, wc+8)] by cyclic whole-own-segment repetition
    joined by "; ", never cutting inside a segment; degenerate no-pad allowed
    in-band; FAIL-CLOSED with KNULL_ERR_PAD_* (band landing, segment-set
    equality, LC1, uniqueness). Feasibility MEASURED 108/108 on the v4 bytes
    (poc/knull/freeze-prep/flops-recheck-v4.json);
  - per-gloss segment floor relaxed to >=1 for plain and plain-padded
    (kernel is the pinned record set; opaque keeps >=2) — ASM-1080;
  - the build-time word band is DROPPED for plain and ENFORCED for
    plain-padded against the kernel gloss (ASM-1082/1085; the FLOP-parity
    role of the old L-3 band moves to the plain-padded arm);
  - renders FOUR item files (kernel, plain, plain-padded, opaque) with joint
    substitution across all four arms and LC8 fail-closed; type mix
    re-derived (expected to shift: all 108 v4 definitions are
    single-segment) and REQUIRED identical across arms;
  - DECISION-ISOMORPHISM (ASM-1082): every builder decision that reads the
    plain gloss (claim segment selection in claim-true/claim-false) uses the
    hash key of the PLAIN arm for the plain-padded arm too; combined with the
    enforced segment-set equality this makes plain and plain-padded items
    differ ONLY where the full gloss is injected (def-match option texts,
    term-match question texts) — claims are byte-identical, enforced
    fail-closed post-build (KNULL_ERR_PAD_PAIRING);
  - writes every output under poc/knull/inputs-v4/ (stores/, items/,
    manifest.json); no new spot-check file is emitted — the maintainer blind
    style sign-off on this store already exists and is pinned
    (poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md);
  - VERSION 4.0.0, GENERATED 2026-07-13.

GEN_SEED, skeleton schedule, leak checks, pairing, opaque/kernel store logic
and all rendering are byte-carried from v2 (so the opaque store bytes are
IDENTICAL to inputs-v2 and the v2 G-3 opaque measurement carries; freeze-prep
G-2 note). Original v1/v2 design rationale: see build_inputs.py /
build_inputs_v2.py docstrings and docs/design-knull-content-injection-
ablation.md (content-injection map).

FAIL-CLOSED: any violation aborts with KNULL_ERR_*; nothing is written.

Usage: python3 poc/knull/build_inputs_v4.py     ($0, CPU-only, deterministic)
"""

import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SCHEMA = "kot-knull-inputs/1"
VERSION = "4.0.0"
GENERATED = "2026-07-13"                    # fixed build date, never wall-clock
GEN_SEED = "knull/1|knull-content-injection-ablation|20260710"
SLOTS_PER_CONCEPT = 10                      # 108 concepts x 10 = 1080 skeletons
N_ITEMS = 1000                              # rank-prefix consumed by the runner
MIN_SEGMENT_CHARS = 15                      # = build-dqa.py contract
FALSE_CLAIM_JACCARD_MAX = 0.5
WORDBAND_FRAC = 0.25                        # kernel-gloss band (ASM-1082 rule)
# Opaque word-target calibration (G-3) — byte-carried from v2; see the
# derivation note in build_inputs_v2.py (nonce syllables tokenize ~2.09x NSM
# English under the pinned SmolLM2 tokenizer; inputs-v2/g3-token-band.json).
OPAQUE_TOKEN_CALIB = 0.48
ARMS = ("kernel", "plain", "plain-padded", "opaque")
TYPE_CYCLE = ("def-match", "term-match", "claim-true", "claim-false")
PLAIN_AUTHORED = "plain-authored.json"      # inputs-v4/, accepted v4.0.0
# The ACCEPTED store pin (maintainer issue-17 acceptance; freeze-prep README):
V4_SHA256 = "97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2"
# Segment floor per arm (ASM-1080: >=1 for plain/plain-padded; opaque keeps
# the v1 contract's >=2; kernel is the pinned record set, not re-generated):
SEGMENT_FLOOR = {"plain": 1, "plain-padded": 1, "opaque": 2}


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


# --- deterministic hash helpers (VERBATIM from build_inputs_v2.py, which
# --- carries them VERBATIM from data/d-qa-r/build-dqar.py, GEN_SEED salt) ----

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


def decision_arm(a):
    """ASM-1082 decision-isomorphism: the plain-padded arm re-uses the PLAIN
    arm's hash keys for every decision that reads the gloss, so the two arms
    make bitwise-identical builder decisions and differ only in injected
    store bytes."""
    return "plain" if a == "plain-padded" else a


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
    """TOKEN-calibrated opaque word target (byte-carried from v2; gate G-3)."""
    return max(6, int(round(word_count(concept["gloss"]) * OPAQUE_TOKEN_CALIB)))


def opaque_gloss(concept):
    """Semantically empty nonce definition — byte-carried from v2 (same
    GEN_SEED => the opaque store bytes are identical to inputs-v2, so the
    MEASURED v2 G-3 opaque token numbers carry; freeze-prep G-2)."""
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


def pad_gloss(base, kernel_gloss):
    """ASM-1082 plain-padded generator rule — logic byte-identical to the
    pinned poc/knull/project_tokens_optionb.py::pad_gloss (and to the G-2
    recompute poc/knull/freeze-prep/flops_recheck_v4.py, which MEASURED
    feasibility 108/108 on the v4 bytes): cyclic whole-own-segment repetition
    joined by "; " into the kernel word band [0.75*wc, max(1.25*wc, wc+8)];
    never cuts inside a segment; degenerate no-pad allowed in-band.
    Returns (padded_gloss, status) or (None, failure_status)."""
    segs = segments(base)
    if not segs:
        return None, "NO_SEGMENTS"
    k = word_count(kernel_gloss)
    lo, hi = k * (1 - WORDBAND_FRAC), max(k * (1 + WORDBAND_FRAC), k + 8)
    g = base
    if word_count(g) > hi:
        return None, "OVER_BAND_UNPADDED"
    i = 0
    while word_count(g) < lo:
        nxt = segs[i % len(segs)]
        if word_count(g) + word_count(nxt) > hi:
            landing = [s for s in segs
                       if lo <= word_count(g) + word_count(s) <= hi]
            if not landing:
                return None, "GAP_NO_LANDING_SEGMENT"
            nxt = landing[0]
            g = g + "; " + nxt
            break
        g = g + "; " + nxt
        i += 1
    if not (lo <= word_count(g) <= hi):
        return None, "OUT_OF_BAND_AFTER_PAD"
    if segments(g) != segs:
        return None, "SEGMENT_SET_CHANGED"
    return g, ("DEGENERATE_NO_PAD" if g == base else "PADDED")


def load_plain_authored():
    """The ACCEPTED v4 plain store: sha-pinned fail-closed, then gated by the
    Option-B relaxed G-1 contract (lint_plain_store_v4.py, run as the pinned
    gate script so the enforced/relaxed split is EXACTLY the ruling's).
    Returns (definitions, manifest_block)."""
    path = os.path.join(HERE, "inputs-v4", PLAIN_AUTHORED)
    got = file_sha256(path)
    if got != V4_SHA256:
        die("KNULL_ERR_STORE_PIN",
            "inputs-v4/%s sha256 %s != accepted pin %s (maintainer issue-17 "
            "acceptance)" % (PLAIN_AUTHORED, got[:12], V4_SHA256[:12]))
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "lint_plain_store_v4.py")],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout)
        sys.stderr.write(r.stderr)
        die("KNULL_ERR_PLAIN_LINT",
            "v4 store failed lint_plain_store_v4 (Option-B relaxed G-1 "
            "contract) — see findings above")
    with open(path, encoding="utf-8") as f:
        authored = json.load(f)
    block = {
        "path": "poc/knull/inputs-v4/%s" % PLAIN_AUTHORED,
        "sha256": got,
        "accepted_pin_verified": True,
        "acceptance": ("maintainer issue-17 acceptance + blind style "
                       "sign-off 10/10 (poc/knull/inputs-v3/"
                       "plain-spotcheck-current-RESULT.md)"),
        "authoring_disclosure": authored["authoring_disclosure"],
        "lint": ("poc/knull/lint_plain_store_v4.py PASS (Option-B relaxed "
                 "contract: L-3 dropped, L-4 relaxed to >=1 admissible "
                 "segment, all other G-1 checks enforced; ASM-1080) — "
                 "re-run fail-closed at this build"),
    }
    return authored["definitions"], block


def build_padded_defs(concepts, plain_defs):
    """The ASM-1082 plain-padded store texts, all checks FAIL-CLOSED
    (KNULL_ERR_PAD_*). Returns (padded_defs, status_counts)."""
    padded, statuses = {}, {}
    for c in concepts:
        base = plain_defs[c["label"]]
        g, status = pad_gloss(base, c["gloss"])
        if g is None:
            die("KNULL_ERR_PAD_%s" % status,
                "plain-padded/%s: generator failed (%s)" % (c["label"], status))
        if segments(g) != segments(base):
            die("KNULL_ERR_PAD_SEGMENTS",
                "plain-padded/%s: segment set changed by padding" % c["label"])
        if word_in(c["label"], g):
            die("KNULL_ERR_PAD_LC1",
                "plain-padded/%s: own label in padded gloss" % c["label"])
        padded[c["label"]] = g
        statuses[status] = statuses.get(status, 0) + 1
    if len(set(padded.values())) != len(padded):
        seen = {}
        for lab, g in padded.items():
            if g in seen:
                die("KNULL_ERR_PAD_UNIQUE",
                    "plain-padded: duplicate padded gloss (%s == %s)"
                    % (lab, seen[g]))
            seen[g] = lab
    return padded, statuses


# ------------------------------------------------------------- store assembly

def build_stores(concepts):
    stores = {a: {} for a in ARMS}
    for c in concepts:
        stores["kernel"][c["label"]] = {
            "urn": c["urn"], "gloss": c["gloss"],
            "record_path": c["record_path"], "record_sha256": c["record_sha256"],
            "records_root": "REPO_ROOT",
        }
    plain_defs, authored_block = load_plain_authored()
    if sorted(plain_defs) != sorted(c["label"] for c in concepts):
        die("KNULL_ERR_COVERAGE", "v4 store labels != covered concept labels")
    padded_defs, pad_statuses = build_padded_defs(concepts, plain_defs)
    stores["_plain_authored_block"] = authored_block
    stores["_pad_statuses"] = pad_statuses
    seen = {"plain": set(), "plain-padded": set(), "opaque": set()}
    for arm, gen, ref_words in (
            # plain: word band DROPPED (Option-B ruling, ASM-1080); floor >=1
            ("plain", lambda c: plain_defs[c["label"]], None),
            # plain-padded: band ENFORCED vs the kernel gloss (ASM-1082/1085)
            ("plain-padded", lambda c: padded_defs[c["label"]],
             lambda c: word_count(c["gloss"])),
            # opaque: word band vs the TOKEN-calibrated target (G-3; v2 carry)
            ("opaque", opaque_gloss, opaque_target_words)):
        adir = os.path.join(HERE, "inputs-v4", "stores", arm)
        os.makedirs(adir, exist_ok=True)
        for c in concepts:
            gl = gen(c)
            if gl in seen[arm]:
                die("KNULL_ERR_DUPGLOSS", "%s store: duplicate gloss (%s)"
                    % (arm, c["label"]))
            seen[arm].add(gl)
            if word_in(c["label"], gl):
                die("KNULL_ERR_LC1", "%s/%s: own label in gloss" % (arm, c["label"]))
            if ref_words is not None:
                wc, wn = ref_words(c), word_count(gl)
                if not (wc * (1 - WORDBAND_FRAC) <= wn <= max(
                        wc * (1 + WORDBAND_FRAC), wc + 8)):
                    die("KNULL_ERR_WORDBAND",
                        "%s/%s: %d words vs reference %d (band %.0f%%)"
                        % (arm, c["label"], wn, wc, WORDBAND_FRAC * 100))
            if len(segments(gl)) < SEGMENT_FLOOR[arm]:
                die("KNULL_ERR_SEGMENTS", "%s/%s: <%d admissible claim segment(s)"
                    % (arm, c["label"], SEGMENT_FLOOR[arm]))
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
                "records_root": "poc/knull/inputs-v4/stores/%s" % arm,
            }
    return stores


# ------------------------------------------------------------- item rendering

def option_order(sid, v, sources):
    """Shared-coordinate option shuffle: sort by hash of the option's SOURCE
    concept urn (not its text), so all arms get the IDENTICAL A-D layout."""
    keyed = sorted(sources, key=lambda s: hhex("%s|v%d|opt|%s" % (sid, v, s[0])))
    return keyed


def build_items(concepts, stores, taken_logged, checks):
    items = {a: [] for a in ARMS}
    taken = {a: set(taken_logged)
             for a in ARMS}   # LC8 vs logged surfaces enforced for EVERY arm
    for slot in range(1, SLOTS_PER_CONCEPT + 1):
        for ci, c in enumerate(concepts):
            sid = "knull:%s:s%d" % (c["label"], slot)
            typ = TYPE_CYCLE[(slot - 1) % len(TYPE_CYCLE)]
            built = try_build(sid, typ, ci, c, concepts, stores,
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


def try_build(sid, typ, ci, c, concepts, stores, taken, checks):
    """Render one skeleton in ALL FOUR arms; None on structural failure.
    Joint substitution ladder (v2-carried): term-match -> def-match;
    claim-true -> claim-false."""
    if typ == "term-match":
        r = render_term_match(sid, ci, c, concepts, stores, taken, checks)
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


def render_term_match(sid, ci, c, concepts, stores, taken, checks):
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
        # ASM-1082 decision-isomorphism: plain-padded uses the PLAIN key
        start = h("%s|segstart|%s" % (sid, decision_arm(a))) % len(segs)
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
            # ASM-1082 decision-isomorphism: plain-padded uses the PLAIN key
            claim = dsegs[h("%s|dseg|%d|%s" % (sid, t, decision_arm(a)))
                          % len(dsegs)]
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
    os.makedirs(os.path.join(HERE, "inputs-v4", "items"), exist_ok=True)
    concepts = load_covered()
    taken_logged = load_logged_prompt_hashes()
    checks = {"lc1_checked": 0, "lc1_substituted": 0, "lc3_accepted": 0,
              "lc3_rejected": 0, "lc4_option_sets": 0, "lc6_true_claims": 0,
              "lc8_retries": 0, "substitutions": []}
    stores = build_stores(concepts)
    authored_block = stores.pop("_plain_authored_block")
    pad_statuses = stores.pop("_pad_statuses")
    items = build_items(concepts, stores, taken_logged, checks)

    pins = {}
    for a in ARMS:
        path = os.path.join(HERE, "inputs-v4", "items", "%s.jsonl" % a)
        with open(path, "w", encoding="utf-8") as f:
            for it in items[a]:
                f.write(json.dumps(it, sort_keys=True,
                                   separators=(",", ":")) + "\n")
        pins["items_%s_sha256" % a] = file_sha256(path)
    for a in ("plain", "plain-padded", "opaque"):
        adir = os.path.join(HERE, "inputs-v4", "stores", a)
        pins["store_%s" % a] = {
            name: file_sha256(os.path.join(adir, name))
            for name in sorted(os.listdir(adir)) if name.endswith(".json")}

    # cross-arm pairing invariants (fail-closed):
    #  (i) identical skeleton_uid sequences and item types across ALL arms
    seqs = [tuple(it["skeleton_uid"] for it in items[a]) for a in ARMS]
    if len(set(seqs)) != 1:
        die("KNULL_ERR_PAIRING", "skeleton sequences differ across arms")
    tmixes = [tuple(it["type"] for it in items[a]) for a in ARMS]
    if len(set(tmixes)) != 1:
        die("KNULL_ERR_PAIRING", "item type sequences differ across arms")
    #  (ii) ASM-1082 decision-isomorphism: plain vs plain-padded differ ONLY
    #  where the full gloss is injected — claims byte-identical
    for ip, iq in zip(items["plain"], items["plain-padded"]):
        if ip["type"] != iq["type"] or ip["answer"] != iq["answer"] \
           or ip.get("claim") != iq.get("claim") \
           or ip.get("claim_source") != iq.get("claim_source"):
            die("KNULL_ERR_PAD_PAIRING",
                "plain vs plain-padded decision divergence at %s"
                % ip["skeleton_uid"])
        if ip["type"] in ("claim-true", "claim-false") \
           and ip["question"] != iq["question"]:
            die("KNULL_ERR_PAD_PAIRING",
                "plain vs plain-padded claim question differs at %s"
                % ip["skeleton_uid"])
    type_mix = {}
    for t in tmixes[0]:
        type_mix[t] = type_mix.get(t, 0) + 1

    manifest = {
        "schema": SCHEMA, "version": VERSION, "generated": GENERATED,
        "generator_seed": GEN_SEED,
        "design_doc": "docs/design-knull-content-injection-ablation.md",
        "optionb_design_doc": "docs/next/design/knull-optionb-analysis.md",
        "asm_block": "ASM-1080..1088 (registered)",
        "n_skeletons": len(seqs[0]), "n_items_planned_per_arm": N_ITEMS,
        "arms": list(ARMS),
        "plain_store_placeholder": False,
        "plain_store_note": ("ACCEPTED v4 Option-B concise store (maintainer "
                             "issue-17 acceptance + blind style sign-off "
                             "10/10, poc/knull/inputs-v3/"
                             "plain-spotcheck-current-RESULT.md); word band "
                             "DROPPED for this arm (ASM-1080/1085); gate G-1 "
                             "= relaxed contract lint_plain_store_v4.py, "
                             "re-run fail-closed at this build."),
        "plain_store_authored": authored_block,
        "plain_padded_generator": {
            "rule": ("ASM-1082: cyclic whole-own-segment repetition joined "
                     "by '; ' into the kernel-gloss word band [0.75*wc, "
                     "max(1.25*wc, wc+8)]; degenerate no-pad allowed "
                     "in-band; fail-closed KNULL_ERR_PAD_* (band landing, "
                     "segment-set equality, LC1, uniqueness); deterministic "
                     "transform of the quality-gated concise store — no "
                     "authoring gate (ASM-1087); disclosed bias direction: "
                     "any answer-key-repetition effect favors the padded "
                     "arm, conservative against the content claim"),
            "status_counts": pad_statuses,
            "cells": ("alone-R1 + verify-retry-R1 only, seeds {0,1,2}, same "
                      "1000 rank-prefix skeletons; excluded from the "
                      "alone-R3 bridge and the shuffled control (ASM-1086)"),
        },
        "opaque_token_calibration": {
            "factor": OPAQUE_TOKEN_CALIB,
            "why": ("byte-carried from v2 (same GEN_SEED => identical opaque "
                    "store bytes); nonce syllable words tokenize at ~2.09x "
                    "NSM English under the pinned SmolLM2 tokenizer; "
                    "measured artifact poc/knull/inputs-v2/"
                    "g3-token-band.json (gate G-3)")},
        "kernel_store": "existing pinned records (data/kernel-v0 + "
                        "data/molecules-v0); records_root = repo root",
        "leak_checks": {k: v for k, v in checks.items() if k != "substitutions"},
        "substitutions_n": len(checks["substitutions"]),
        "substitutions": checks["substitutions"][:50],
        "type_mix": type_mix,
        "type_mix_note": ("re-derived on the v4 store and REQUIRED identical "
                          "across all four arms (enforced fail-closed); "
                          "expected shift vs v2: all 108 v4 definitions are "
                          "single-segment (claim-true scarcity disclosed)"),
        "provenance_pins": {
            "f2b_runner_py_sha256": file_sha256(
                os.path.join(ROOT, "poc", "f2b", "runner", "f2b_runner.py")),
            "f2b_manifest_sha256": file_sha256(
                os.path.join(ROOT, "poc", "f2b", "inputs", "f2b-manifest.json")),
            "build_dqar_py_sha256": file_sha256(
                os.path.join(ROOT, "data", "d-qa-r", "build-dqar.py")),
            "lint_plain_store_py_sha256": file_sha256(
                os.path.join(HERE, "lint_plain_store.py")),
            "lint_plain_store_v4_py_sha256": file_sha256(
                os.path.join(HERE, "lint_plain_store_v4.py")),
        },
        "pins": pins,
    }
    mpath = os.path.join(HERE, "inputs-v4", "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")

    print("knull v4 inputs built: %d skeletons x %d arms; type mix %s; "
          "padded %s; manifest %s"
          % (len(seqs[0]), len(ARMS),
             json.dumps(type_mix, sort_keys=True),
             json.dumps(pad_statuses, sort_keys=True), mpath))
    print("manifest sha256: %s" % file_sha256(mpath))


if __name__ == "__main__":
    main()
