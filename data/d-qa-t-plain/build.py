#!/usr/bin/env python3
"""build d-qa-t-plain AND d-qa-t-opaque — the gsx0 store-injection corpora
(generic-store-external-gold; docs/next/design/generic-store-external-gold.md
section 4.1; readiness-review revision R7 "implement, validate, and pin the
corpora before preregistration").

ONE deterministic pass builds BOTH corpora, so the item skeletons are
IDENTICAL ACROSS STORE CONDITIONS BY CONSTRUCTION (the portfolio-assessment
Rank-4 requirement): every polarity decision and donor coordinate is computed
ONCE (on the plain store, the binding constraint) and consumed verbatim by the
opaque rendering. data/d-qa-t-opaque/build.py is a thin shim executing this
file.

CONSTRUCTION (design section 4.1, with two disclosed rulings):

  For each of the 360 committed data/d-qa-t/items/covered.jsonl items the
  skeleton is HELD FIXED — concept, template type, answer slot, distractor /
  donor concept coordinates, option-slot layout, pinned rank — and every
  rendered kernel gloss is substituted with the SAME concept's gloss from the
  injected store (plain-padded = the token-matched plain dictionary, 0.99x;
  opaque = the token-matched nonce store, 1.00x; both from the knull-v2
  verdict-backing poc/knull/inputs-v4/stores tree, byte-pinned below).

  RULING G-1 (mapping, supersedes the earlier "regenerate from the d-qa-t
  generator seed" wording): option-slot -> concept is recovered by EXACT,
  UNIQUE, full-byte gloss match against the 108-concept pool, after (a) the
  d-qa-t corpus reproduces its frozen f2b-transfer pin byte-for-byte and
  (b) pool-gloss uniqueness is asserted (108/108 unique, fail-closed). This
  is equivalent to regeneration (the committed corpus IS the pinned generator
  output) and fails closed on any ambiguity; it is not text-similarity
  reverse-engineering.

  RULING G-2 (claim polarity substitution, MEASURED constraint): the
  plain-padded store has EXACTLY ONE unique admissible (>=15-char) segment
  per concept (padding is cyclic self-repetition; segments() dedups), so a
  concept carrying TWO claim-true skeletons cannot render two distinct plain
  claim-true surfaces. Pre-committed rule: items are processed in pinned rank
  order; the FIRST claim-true item of a concept receives the (seeded-offset)
  store segment; any LATER claim-true item of the same concept SUBSTITUTES to
  claim-false via the seeded donor draw below — identically in BOTH store
  corpora (13 items at build time; counts disclosed in leak-check.json;
  answer flips yes->no vs the kernel skeleton on exactly those items, a
  disclosed deviation — plain and opaque stay skeleton-identical, which is
  the binding requirement; item-level pairing to the KERNEL corpus is
  explicitly not claimed by the design).

  claim-false rendering: donor concept HELD FIXED from the committed item's
  claim_source; the claim is the donor's store-gloss segment at a seeded
  start offset, admissible under LC3-s (not a substring of the target's
  store gloss; token-Jaccard < 0.5 vs the target's store gloss) and
  prompt-fresh; if NO segment of the fixed donor is admissible on the PLAIN
  store, the donor is redrawn by the seeded loop (disclosed count) and the
  redrawn donor binds BOTH stores. Opaque rendering may never redraw
  independently: an opaque-side admissibility failure aborts the build
  (GSX0_ERR_INJ — skeleton forks are not allowed).

DETERMINISM: no wall-clock, no os.urandom, no Python hash(); every choice is
a function of sha256 over the pre-committed gsx0 seeds + fixed strings + the
byte-pinned sources. NO LLM authored, selected, or edited any item text.
FAIL-CLOSED: any pin mismatch, coverage gap, mapping ambiguity, leak-check
violation, or admissibility exhaustion aborts with a named GSX0_ERR_* /
DQAT_ERR_* message; nothing is written on failure.

Gates enforced here (design section 4.1): G-COVER (every concept in any
option/claim has a store record), G-LC8p (full-prompt-surface disjointness
from ALL 650 d-qa + 1000 d-qa-r + 360 d-qa-t items and between the two new
corpora), LC1-s/LC2/LC3-s/LC4/LC5/LC7 store analogues. G-TOK (the exact
SmolLM2-135M token band) is the SEPARATE pinned gate poc/gsx0/gtok_check.py
(stdlib-only corpora stay reproducible without the tokenizers wheel).

Usage:  python3 data/d-qa-t-plain/build.py   (from anywhere; single draw)
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
import kot_common as kc  # noqa: E402  (corpus_hash — kot-corpus-hash/1 reference impl)

GENERATED = "2026-07-15"            # fixed build date (determinism: never wall-clock)
SCHEMA = "kot-dqat-store/1"
VERSION = "0.1.0"
# THE seeds, pre-committed verbatim in the design (section 4.1):
SEEDS = {"plain": "gsx0-plain/1|generic-store-external-gold|20260713",
         "opaque": "gsx0-opaque/1|generic-store-external-gold|20260713"}
N_ITEMS = 360
MIN_SEGMENT_CHARS = 15              # = build-dqat.py (canonical rendering contract)
FALSE_CLAIM_JACCARD_MAX = 0.5

# ---- byte pins (fail-closed; values = the frozen f2b-transfer registry pins
# and the knull-v2 verdict-backing store tree, design section 12 B-1) --------
DQAT_PIN = "7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27"
KERNEL_V0_PIN = "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809"
MOLECULES_V0_PIN = "69f0c8a354ce489d15e9156d611932ba548f80c41e78af4ffe597192067a59c4"
REF_PINS = {  # LC8p reference corpora (same values as build-dqat.py)
    "d-qa": "ad756a7e31f9281de3baaff149e87832d8195452b41b19b6f16883ff196571e6",
    "d-qa-r": "0d548bf18ac78f9d7b2abb6686c567f0930acd494c5ca03cee49806c4996ec5e",
}
STORE_MANIFEST_SHA = "ae52862d9f95c83238230ed555628318140f69f9c456eb95fc82b25fcac2ebfe"
PLAIN_AUTHORED_SHA = "97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2"
STORE_ROOT = os.path.join("poc", "knull", "inputs-v4", "stores")
STORES = {"plain": "plain-padded", "opaque": "opaque"}   # arm-name -> store dir
OUT_DIRS = {"plain": os.path.join(ROOT, "data", "d-qa-t-plain"),
            "opaque": os.path.join(ROOT, "data", "d-qa-t-opaque")}
ID_PREFIX = {"plain": "dqatp:", "opaque": "dqato:"}

TOKEN_RE = re.compile(r"[a-z]+")
URN_MARKUP_RE = re.compile(r"\{urn:[^|}]+\|([^}]*)\}")
TERM_Q_TPL = 'A word whose definition is: "%s". Which word is it?'


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def h_seed(seed, s):
    return int.from_bytes(hashlib.sha256(("%s|%s" % (seed, s)).encode("utf-8")).digest(), "big")


def qhash(question, options):
    """UNSALTED prompt-surface hash — comparable across d-qa/d-qa-r/d-qa-t and
    the two new corpora (verbatim build-dqat.py construction)."""
    blob = question + "||" + "|".join(o["text"] for o in (options or []))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def tokens(text):
    return set(TOKEN_RE.findall(text.lower()))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def word_in(word, text):
    return re.search(r"\b%s\b" % re.escape(word.lower()), text.lower()) is not None


def render_plain(text):
    """VERBATIM build-dqa.py normalisation (canonical-record rendering)."""
    text = URN_MARKUP_RE.sub(r"\1", text)
    text = text.replace(" [m]", "").replace("[m]", "")
    return re.sub(r"  +", " ", text).strip()


def segments(gloss):
    """VERBATIM build-dqa.py claim segmentation (dedup => the plain-padded
    cyclic repetition contributes each segment ONCE)."""
    out = []
    for seg in re.split(r"[.;]", gloss):
        seg = seg.strip()
        if len(seg) >= MIN_SEGMENT_CHARS and '"' not in seg and seg not in out:
            out.append(seg)
    return out


def claim_question(label, claim):
    return ('According to the definition of "%s", is the following true of %s? '
            '"%s" Answer yes or no.' % (label, label, claim))


# --------------------------------------------------------------- load sources

def verify_pins():
    for corpus, pin in (("d-qa-t", DQAT_PIN), ("kernel-v0", KERNEL_V0_PIN),
                        ("molecules-v0", MOLECULES_V0_PIN),
                        ("d-qa", REF_PINS["d-qa"]), ("d-qa-r", REF_PINS["d-qa-r"])):
        got = kc.corpus_hash(ROOT, corpus)
        if got != pin:
            die("GSX0_ERR_REFPIN", "%s corpus hash %s != pinned %s" % (corpus, got, pin))
    for rel, want in ((os.path.join("poc", "knull", "inputs-v4", "manifest.json"), STORE_MANIFEST_SHA),
                      (os.path.join("poc", "knull", "inputs-v4", "plain-authored.json"), PLAIN_AUTHORED_SHA)):
        got = file_sha256(os.path.join(ROOT, rel))
        if got != want:
            die("GSX0_ERR_REFPIN", "%s sha256 %s != pinned %s (knull-v2 "
                "verdict-backing store tree drifted)" % (rel, got, want))


def load_pool():
    """The 108-concept pool with KERNEL glosses (for slot->concept mapping)."""
    pool = {}
    kdir = os.path.join(ROOT, "data", "kernel-v0", "concepts")
    for name in sorted(os.listdir(kdir)):
        if name.endswith(".json"):
            rec = json.load(open(os.path.join(kdir, name), encoding="utf-8"))
            pool[rec["label"]] = {"label": rec["label"], "urn": rec["id"],
                                  "gloss": rec["gloss"].strip()}
    mdir = os.path.join(ROOT, "data", "molecules-v0", "molecules")
    for name in sorted(os.listdir(mdir)):
        if name.endswith(".json"):
            rec = json.load(open(os.path.join(mdir, name), encoding="utf-8"))
            pool[rec["label"]] = {"label": rec["label"], "urn": rec["id"],
                                  "gloss": render_plain(rec["groundingNote"])}
    if len(pool) != 108:
        die("GSX0_ERR_SOURCE", "expected 108 pool concepts, got %d" % len(pool))
    glosses = [c["gloss"] for c in pool.values()]
    if len(set(glosses)) != len(glosses):
        die("GSX0_ERR_MAP", "kernel pool glosses are not unique — the exact-match "
            "slot->concept mapping (RULING G-1) is ambiguous; aborting")
    return pool


def load_store(store_dir):
    """label -> {gloss, id, path, sha256} for one knull store."""
    out = {}
    full = os.path.join(ROOT, STORE_ROOT, store_dir)
    for name in sorted(os.listdir(full)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(full, name)
        rec = json.load(open(path, encoding="utf-8"))
        out[rec["label"]] = {
            "gloss": rec["gloss"], "id": rec["id"],
            "record_path": "/".join([STORE_ROOT.replace(os.sep, "/"), store_dir, name]),
            "record_sha256": file_sha256(path)}
    if len(out) != 108:
        die("GSX0_ERR_SOURCE", "store %s: expected 108 records, got %d" % (store_dir, len(out)))
    glosses = [r["gloss"] for r in out.values()]
    if len(set(glosses)) != len(glosses):
        die("GSX0_ERR_INJ", "store %s glosses not unique — LC4 injection unsafe" % store_dir)
    return out


def load_ref_prompt_hashes():
    """LC8p reference set: every d-qa (650) + d-qa-r (1000) + d-qa-t (360)
    prompt surface (pins verified in verify_pins)."""
    taken = set()
    counts = {"d-qa": ("items", ("covered.jsonl", "control.jsonl"), 650),
              "d-qa-r": ("items", ("covered.jsonl",), 1000),
              "d-qa-t": ("items", ("covered.jsonl",), 360)}
    for corpus, (sub, files, want) in sorted(counts.items()):
        n = 0
        for name in files:
            with open(os.path.join(ROOT, "data", corpus, sub, name), encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        it = json.loads(line)
                        taken.add(qhash(it["question"], it["options"]))
                        n += 1
        if n != want:
            die("GSX0_ERR_SOURCE", "expected %d %s reference items, got %d" % (want, corpus, n))
    return taken


# --------------------------------------------------------------- injection

def pick_segment(seed, key, segs, target_gloss_lc, target_toks, working, label,
                 lc3=False, checks=None):
    """Seeded-start scan over segs for an admissible, prompt-fresh claim.
    Returns claim or None. lc3=True applies the LC3-s non-entailment checks."""
    if not segs:
        return None
    start = h_seed(seed, "%s|segstart" % key) % len(segs)
    for j in range(len(segs)):
        claim = segs[(start + j) % len(segs)]
        if lc3:
            if claim.lower() in target_gloss_lc:
                if checks is not None:
                    checks["lc3_rejected"] += 1
                continue
            if jaccard(tokens(claim), target_toks) >= FALSE_CLAIM_JACCARD_MAX:
                if checks is not None:
                    checks["lc3_rejected"] += 1
                continue
        if qhash(claim_question(label, claim), None) in working:
            continue
        return claim
    return None


def build():
    verify_pins()
    pool = load_pool()
    gloss_to_label = {c["gloss"]: c["label"] for c in pool.values()}
    stores = {arm: load_store(sdir) for arm, sdir in STORES.items()}

    items_kernel = []
    with open(os.path.join(ROOT, "data", "d-qa-t", "items", "covered.jsonl"),
              encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items_kernel.append(json.loads(line))
    if len(items_kernel) != N_ITEMS:
        die("GSX0_ERR_SOURCE", "d-qa-t items %d != %d" % (len(items_kernel), N_ITEMS))
    items_kernel.sort(key=lambda it: it["rank"])  # pinned rank order (RULING G-2)

    # G-COVER: every concept in any option/claim of the 360 skeletons.
    needed = set()
    for it in items_kernel:
        needed.add(it["label"])
        if it["options"] and it["type"] == "def-match":
            for o in it["options"]:
                if o["text"] not in gloss_to_label:
                    die("GSX0_ERR_MAP", "def-match option text in %s has no exact "
                        "unique kernel-gloss match (RULING G-1)" % it["id"])
                needed.add(gloss_to_label[o["text"]])
        if it["options"] and it["type"] == "term-match":
            for o in it["options"]:
                if o["text"] not in pool:
                    die("GSX0_ERR_MAP", "term-match option label %r in %s not in "
                        "the pool" % (o["text"], it["id"]))
                needed.add(o["text"])
        if it["type"] == "claim-false":
            needed.add(it["claim_source"])
    for arm in STORES:
        missing = sorted(needed - set(stores[arm]))
        if missing:
            die("ERR_STORE_COVER", "store %s missing records for %s" % (arm, missing))

    ref_hashes = load_ref_prompt_hashes()
    labels_sorted = sorted(pool)

    # PASS 1 (plain, the binding store): fix polarity + donor decisions.
    # PASS 2 (opaque): consume the identical decisions.
    decisions = {}          # skeleton_id -> {"polarity","donor"}
    out_items = {"plain": [], "opaque": []}
    checks = {arm: {"lc1s_checked": 0, "lc2_checked": 0, "lc3_rejected": 0,
                    "lc4_option_sets": 0, "true_claims": 0,
                    "polarity_substituted": [], "donor_redrawn": [],
                    "lc8p_working_hits": 0}
              for arm in STORES}
    working = {arm: set(ref_hashes) for arm in STORES}
    claim_true_used = {arm: set() for arm in STORES}   # concepts already holding a claim-true

    for arm in ("plain", "opaque"):
        seed = SEEDS[arm]
        store = stores[arm]
        chk = checks[arm]
        for it in items_kernel:
            sid = it["id"]
            label = it["label"]
            srec = store[label]
            new = {
                "id": ID_PREFIX[arm] + sid.split(":", 1)[1],
                "skeleton_id": sid,
                "slice": "covered",
                "label": label,
                "urn": srec["id"],
                "aligned_to": it["urn"],
                "source": STORES[arm],
                "record_path": srec["record_path"],
                "record_sha256": srec["record_sha256"],
                "kernel_checkable": True,
                "gloss_doc_id": "doc:%s:%s" % (STORES[arm], label),
                "rank": it["rank"],
            }
            if it["type"] == "def-match":
                opts = []
                for o in it["options"]:
                    c_label = gloss_to_label[o["text"]]
                    opts.append({"key": o["key"], "text": store[c_label]["gloss"]})
                texts = [o["text"] for o in opts]
                if len(set(texts)) != len(texts):
                    die("GSX0_ERR_INJ", "LC4 duplicate injected option text in %s" % new["id"])
                chk["lc4_option_sets"] += 1
                ans_text = {o["key"]: o["text"] for o in opts}[it["answer"]]
                if ans_text.lower() in it["question"].lower():
                    die("GSX0_ERR_INJ", "LC2 answer text leaked in question %s" % new["id"])
                chk["lc2_checked"] += 1
                new.update(type="def-match", question=it["question"],
                           options=opts, answer=it["answer"])
            elif it["type"] == "term-match":
                if it["question"] != TERM_Q_TPL % pool[label]["gloss"]:
                    die("GSX0_ERR_MAP", "term-match question of %s does not "
                        "reproduce from the kernel gloss template" % sid)
                if word_in(label.split(" (")[0], srec["gloss"]):
                    die("GSX0_ERR_INJ", "LC1-s headword %r appears in the %s store "
                        "gloss — term-match item %s would leak its answer"
                        % (label, arm, new["id"]))
                chk["lc1s_checked"] += 1
                new.update(type="term-match", question=TERM_Q_TPL % srec["gloss"],
                           options=it["options"], answer=it["answer"])
            elif it["type"] in ("claim-true", "claim-false"):
                # --- decide polarity + donor (plain pass binds both stores) --
                if arm == "plain":
                    dec = {"polarity": it["type"], "donor": it.get("claim_source")}
                    if it["type"] == "claim-true" and label in claim_true_used["plain"]:
                        dec["polarity"] = "claim-false"   # RULING G-2 substitution
                        dec["donor"] = None               # donor drawn below
                        chk["polarity_substituted"].append(sid)
                    decisions[sid] = dec
                dec = decisions[sid]
                if dec["polarity"] == "claim-true":
                    claim = pick_segment(seed, sid, segments(srec["gloss"]),
                                         None, None, working[arm], label)
                    if claim is None:
                        die("GSX0_ERR_INJ", "no fresh admissible %s claim-true "
                            "segment for %s (store %s)" % (arm, sid, STORES[arm]))
                    claim_true_used[arm].add(label)
                    chk["true_claims"] += 1
                    new.update(type="claim-true", question=claim_question(label, claim),
                               options=None, answer="yes", claim=claim)
                else:
                    tgt_lc = srec["gloss"].lower()
                    tgt_toks = tokens(srec["gloss"])
                    donor = dec["donor"]
                    claim = None
                    if donor is not None:
                        claim = pick_segment(seed, sid, segments(store[donor]["gloss"]),
                                             tgt_lc, tgt_toks, working[arm], label,
                                             lc3=True, checks=chk)
                    if claim is None:
                        if arm != "plain":
                            # opaque may NEVER fork the skeleton (RULING G-2)
                            die("GSX0_ERR_INJ", "opaque rendering cannot satisfy the "
                                "plain-fixed donor %r for %s" % (donor, sid))
                        # plain donor redraw (seeded; binds both stores)
                        for t in range(256):
                            cand = labels_sorted[h_seed(seed, "%s|donor|%d" % (sid, t)) % len(labels_sorted)]
                            if cand == label or store[cand]["gloss"] == srec["gloss"]:
                                continue
                            claim = pick_segment(seed, "%s|re%d" % (sid, t),
                                                 segments(store[cand]["gloss"]),
                                                 tgt_lc, tgt_toks, working[arm], label,
                                                 lc3=True, checks=chk)
                            if claim is not None:
                                donor = cand
                                break
                        if claim is None:
                            die("GSX0_ERR_INJ", "LC3-s/LC8p: no admissible fresh false "
                                "claim for %s on the plain store" % sid)
                        if donor != dec["donor"]:
                            chk["donor_redrawn"].append(sid)
                            decisions[sid] = {"polarity": "claim-false", "donor": donor}
                    new.update(type="claim-false", question=claim_question(label, claim),
                               options=None, answer="no", claim=claim,
                               claim_source=donor)
            else:
                die("GSX0_ERR_SOURCE", "unknown item type %r in %s" % (it["type"], sid))

            qk = qhash(new["question"], new["options"])
            if qk in working[arm]:
                chk["lc8p_working_hits"] += 1
                die("GSX0_ERR_LEAK", "LC5/LC8p prompt-surface collision for %s "
                    "(against d-qa/d-qa-r/d-qa-t or an earlier item)" % new["id"])
            working[arm].add(qk)
            out_items[arm].append(new)

    # cross-corpus disjointness (plain vs opaque prompt surfaces)
    ph = {qhash(i["question"], i["options"]) for i in out_items["plain"]}
    oh = {qhash(i["question"], i["options"]) for i in out_items["opaque"]}
    if ph & oh:
        die("GSX0_ERR_LEAK", "plain/opaque prompt surfaces overlap (%d)" % len(ph & oh))

    # final leak checks per corpus (LC5 ids, LC7 balance, markup)
    for arm in STORES:
        ids = [i["id"] for i in out_items[arm]]
        if len(set(ids)) != len(ids):
            die("GSX0_ERR_LEAK", "duplicate ids in %s" % arm)
        ans_dist = {}
        for i in out_items[arm]:
            ans_dist[i["answer"]] = ans_dist.get(i["answer"], 0) + 1
            blob = i["question"] + "".join(o["text"] for o in (i["options"] or []))
            if "{urn:" in blob or "[m]" in blob:
                die("GSX0_ERR_MARKUP", "unrendered markup in %s" % i["id"])
        mc_total = sum(v for k, v in ans_dist.items() if k in "ABCD")
        for k in "ABCD":
            if ans_dist.get(k, 0) > mc_total / 2:
                die("GSX0_ERR_LEAK", "LC7 answer-position imbalance in %s: %s=%d/%d"
                    % (arm, k, ans_dist[k], mc_total))
        yn = ans_dist.get("yes", 0) + ans_dist.get("no", 0)
        for k in ("yes", "no"):
            if ans_dist.get(k, 0) > 0.75 * yn:
                die("GSX0_ERR_LEAK", "LC7 yes/no imbalance in %s: %s=%d/%d"
                    % (arm, k, ans_dist.get(k, 0), yn))
        checks[arm]["lc7_answer_distribution"] = {k: ans_dist[k] for k in sorted(ans_dist)}

    # identical-skeleton assertion across the two corpora (the requirement)
    for a, b in zip(out_items["plain"], out_items["opaque"]):
        same = (a["skeleton_id"] == b["skeleton_id"] and a["rank"] == b["rank"]
                and a["type"] == b["type"] and a["answer"] == b["answer"]
                and a["label"] == b["label"]
                and ([o["key"] for o in (a["options"] or [])]
                     == [o["key"] for o in (b["options"] or [])])
                and a.get("claim_source") == b.get("claim_source"))
        if not same:
            die("GSX0_ERR_INJ", "skeleton fork between plain/opaque at %s"
                % a["skeleton_id"])

    # the opaque pass CONSUMES the plain decisions, so its disclosure lists are
    # by construction the plain ones (skeleton identity asserted above)
    checks["opaque"]["polarity_substituted"] = list(checks["plain"]["polarity_substituted"])
    checks["opaque"]["donor_redrawn"] = list(checks["plain"]["donor_redrawn"])

    return pool, stores, out_items, checks, decisions


# --------------------------------------------------------------- write outputs

def wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def wjsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")


def main():
    pool, stores, out_items, checks, decisions = build()
    builder_sha = file_sha256(os.path.abspath(__file__))
    for arm in ("plain", "opaque"):
        corpus = "d-qa-t-%s" % arm
        outdir = OUT_DIRS[arm]
        os.makedirs(os.path.join(outdir, "items"), exist_ok=True)
        wjsonl(os.path.join(outdir, "items", "covered.jsonl"), out_items[arm])
        chk = checks[arm]
        leak = {
            "artifact": "%s-leak-check" % corpus, "generated": GENERATED,
            "result": "PASS", "generator_seed": SEEDS[arm],
            "checks": {
                "G-COVER-store-records-for-every-slot-concept": {"store_records": 108},
                "LC1s-headword-not-in-injected-definition": {"checked": chk["lc1s_checked"], "leaks": 0},
                "LC2-answer-text-not-in-question": {"checked": chk["lc2_checked"]},
                "LC3s-false-claim-not-entailed-by-injected-gloss": {
                    "rule": "false claims must not be a substring of the target's "
                            "STORE gloss and must have token-Jaccard < %s vs it"
                            % FALSE_CLAIM_JACCARD_MAX,
                    "rejected_candidates": chk["lc3_rejected"]},
                "LC4-options-distinct-answer-present": {"option_sets": chk["lc4_option_sets"]},
                "LC5-no-duplicate-ids-or-questions": {"items": len(out_items[arm])},
                "LC7-answer-position-balance": chk["lc7_answer_distribution"],
                "LC8p-prompt-surface-disjoint": {
                    "rule": "no item shares its exact prompt surface (question + "
                            "option texts, unsalted sha256) with any of the 650 d-qa, "
                            "1000 d-qa-r, or 360 d-qa-t items, with an earlier item of "
                            "this corpus, or with the sibling store corpus",
                    "reference_items": {"d-qa": 650, "d-qa-r": 1000, "d-qa-t": 360}},
                "RULING-G2-claim-polarity-substitutions": {
                    "rule": "plain-padded holds EXACTLY ONE unique admissible segment "
                            "per concept (measured), so the second claim-true skeleton "
                            "of a concept substitutes to claim-false (seeded donor), "
                            "identically in both store corpora; answer flips yes->no "
                            "vs the kernel skeleton on exactly these items (disclosed "
                            "deviation; plain/opaque skeleton identity is preserved)",
                    "substituted_skeleton_ids": chk["polarity_substituted"],
                    "count": len(chk["polarity_substituted"])},
                "RULING-G2-donor-redraws": {
                    "rule": "claim-false items whose committed donor has no admissible "
                            "segment on the PLAIN store redraw the donor (seeded); the "
                            "redrawn donor binds BOTH stores",
                    "redrawn_skeleton_ids": chk["donor_redrawn"],
                    "count": len(chk["donor_redrawn"])},
            },
            "note": "fail-closed: any violation aborts the build; this file exists "
                    "only on PASS. G-TOK (exact SmolLM2-135M token band vs the kernel "
                    "d-qa-t surfaces) is the separate pinned gate "
                    "poc/gsx0/gtok_check.py -> poc/gsx0/g3-token-band-gsx0.json.",
        }
        wjson(os.path.join(outdir, "leak-check.json"), leak)
        manifest = {
            "corpus": corpus, "schema": SCHEMA, "version": VERSION,
            "generated": GENERATED, "generator_seed": SEEDS[arm],
            "role": "gsx0 (generic-store-external-gold) inputs: the 360 committed "
                    "d-qa-t item skeletons with every kernel gloss substituted by the "
                    "%s store gloss of the same concept; stage-1 blind external "
                    "adjudication surfaces + the externally-labelled stage-2 eval "
                    "prefix; design docs/next/design/generic-store-external-gold.md "
                    "section 4.1" % STORES[arm],
            "authorship": "deterministically generated by data/d-qa-t-plain/build.py "
                          "(single pass builds BOTH store corpora => identical item "
                          "skeletons across store conditions by construction); NO LLM "
                          "authored, selected, or edited any item text",
            "builder": {"path": "data/d-qa-t-plain/build.py", "sha256": builder_sha},
            "store": {"name": STORES[arm],
                      "root": STORE_ROOT.replace(os.sep, "/") + "/" + STORES[arm],
                      "records": 108,
                      "tree_manifest_sha256": STORE_MANIFEST_SHA,
                      "plain_authored_sha256": PLAIN_AUTHORED_SHA},
            "sources": {
                "d-qa-t-skeletons": {"kot_corpus_hash": DQAT_PIN,
                                     "use": "item skeletons held fixed (concept, template "
                                            "type, answer slot, distractor/donor coordinates, "
                                            "option-slot layout, pinned rank)"},
                "kernel-v0": {"kot_corpus_hash": KERNEL_V0_PIN,
                              "use": "slot->concept mapping only (RULING G-1)"},
                "molecules-v0": {"kot_corpus_hash": MOLECULES_V0_PIN,
                                 "use": "slot->concept mapping only (RULING G-1)"},
                "d-qa-cross-set-reference": {"kot_corpus_hash": REF_PINS["d-qa"],
                                             "use": "LC8p disjointness reference only"},
                "d-qa-r-cross-set-reference": {"kot_corpus_hash": REF_PINS["d-qa-r"],
                                               "use": "LC8p disjointness reference only"},
            },
            "counts": {"covered_items": len(out_items[arm]),
                       "covered_concepts": 108,
                       "by_type": {}},
            "files": {"items/covered.jsonl": "360 injected items, pinned order (rank "
                                             "carried from d-qa-t)",
                      "leak-check.json": "fail-closed gate evidence incl. RULING G-2 "
                                         "substitution disclosure"},
        }
        for i in out_items[arm]:
            key = "covered:%s" % i["type"]
            manifest["counts"]["by_type"][key] = manifest["counts"]["by_type"].get(key, 0) + 1
        wjson(os.path.join(outdir, "manifest.json"), manifest)
        print("%s build OK: %d items (yes %d / no %d; polarity substitutions %d, "
              "donor redraws %d)"
              % (corpus, len(out_items[arm]),
                 chk["lc7_answer_distribution"].get("yes", 0),
                 chk["lc7_answer_distribution"].get("no", 0),
                 len(chk["polarity_substituted"]), len(chk["donor_redrawn"])))


if __name__ == "__main__":
    main()
