#!/usr/bin/env python3
# ENGINE-INF (D2/D3) shared library — divergence-seam construction over the
# certified RULES-1 engine.
#
# Design anchors (every mechanical rule cites its source):
#   docs/next/design/engine-inference-under-typing.md (the DESIGN; §1
#   divergence-seam construction, §1.3 arms, §1.4 items/input grade S,
#   §2 deterministic gold G1-G4 + scoring, §2.3 divergence certificate +
#   primary endpoint, §5 blocking pilot PC-1..PC-5)
#   docs/next/protocol/blocking-pilot-before-freeze.md (kot-pilot/1 contract)
#   ASM-1950..1967 (registered design block) + the BUILD operationalisation
#   block poc/engine-inference/asm-1990-2009.json (owner writer-4):
#   every place where the design left a constant/rule to be fixed at build
#   time carries an ASM-199x citation below.
#
# Engine identity: poc/rules-1/twin_engine.py, UNCHANGED (design §1.1 —
# "no new rule kind, no engine version change" at E0). This library only
# COMPILES inputs for it and READS its closure.
#
# Determinism: no wall-clock, no RNG anywhere; all iteration over sorted
# structures; the K-shuf derangement is a fixed rotation (ASM-1996).
# Fail-closed: unknown/underivable cases raise or are logged exclusions —
# never silently defaulted.

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "poc" / "rules-1"))
from twin_engine import Closure, EngineError, load_tbox  # noqa: E402  (pinned engine)

DICT = ROOT / "data/lexical-wn31/source/dict"
KV1 = ROOT / "data/kernel-v1"
MODULE = ROOT / "data/axioms-engineinf-v0"

LEMMAS = ("break", "find", "friend", "make")          # Stage-A inventory (ASM-1951)
LEMMA_POS = {"break": "v", "find": "v", "friend": "n", "make": "v"}

# ---- shared class vocabulary (data/axioms-engineinf-v0/classes/) ----------
# Bridge classes are minted classDeclarations anchored on WN31's third-party
# physical_entity/abstraction top split (design §1.2). SIDES maps each class
# to its top-split side for the scorer/divergence side-projection (ASM-1994).
C = {k: "urn:kot-engineinf:cls:%s" % k for k in
     ("phys", "abst", "material", "words", "info", "happening", "person",
      "wn-somebody", "wn-something")}
SIDES = {C["phys"]: "phys", C["material"]: "phys", C["person"]: "phys",
         C["abst"]: "abst", C["words"]: "abst", C["info"]: "abst",
         C["happening"]: "abst",
         # WN frame vocabulary: 'somebody' is a person claim (phys side);
         # 'something' asserts NOTHING at G2 granularity (ASM-1994).
         C["wn-somebody"]: "phys", C["wn-something"]: None}

# WN31 top-split noun synsets, MEASURED from the pinned extraction
# (data/lexical-wn31/synsets-noun.jsonl lemma lookup, 2026-07-12):
PHYSICAL_ENTITY = "urn:lexical-wn31:n-00001930"
ABSTRACTION = "urn:lexical-wn31:n-00002137"
PERSON = "urn:lexical-wn31:n-00007846"

PRONOUNS = {"i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
            "us", "them", "this", "these", "those", "that", "one", "who",
            "whom", "himself", "herself", "itself", "themselves", "myself"}
DETERMINERS = {"the", "a", "an", "my", "your", "his", "her", "its", "our",
               "their", "some", "all", "any", "no", "more", "most", "many",
               "much", "each", "every", "both", "few", "several", "two",
               "three", "four", "five", "this", "these", "those", "that",
               "such", "another", "other", "either", "neither", "one"}
NP_STOP = {"of", "to", "in", "on", "for", "with", "at", "by", "from", "into",
           "out", "off", "over", "about", "against", "as", "that", "who",
           "which", "when", "while", "because", "if", "and", "or", "but",
           "not", "so", "than", "like", "after", "before", "just", "up",
           "down", "away", "apart", "is", "was", "were", "are", "be", "been",
           "had", "has", "have", "will", "would", "can", "cannot", "could",
           "do", "does", "did"}
AUX = {"is", "was", "were", "are", "be", "been", "being", "am", "will",
       "would", "can", "cannot", "could", "shall", "should", "may", "might",
       "must", "do", "does", "did", "to", "not", "n't", "had", "has", "have"}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canon_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def wilson_lb(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0
    ph = k / n
    d = 1 + z * z / n
    c = ph + z * z / (2 * n)
    e = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5)
    return (c - e) / d


def binom_tail_ge(k, n, p):
    """P[X >= k] for X~Bin(n,p), exact, iterative (no scipy on this box)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    q = 1.0 - p
    term = q ** n  # P[X=0]
    cdf = 0.0
    for i in range(0, k):
        cdf += term
        term = term * (n - i) / (i + 1) * (p / q) if q > 0 else 0.0
    return max(0.0, 1.0 - cdf)


def clopper_pearson_lb(k, n, alpha=0.05):
    """One-sided exact (Clopper-Pearson) lower confidence bound for a
    binomial proportion, by bisection on the exact tail (deterministic)."""
    if n == 0 or k == 0:
        return 0.0
    lo, hi = 0.0, k / n
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_tail_ge(k, n, mid) >= alpha:
            hi = mid
        else:
            lo = mid
    return lo


# =========================================================== WN31 raw parsing
# All parsing below consumes ONLY the pinned WN31 source bytes
# (data/lexical-wn31/source/dict/*, tarball sha 3f7d8be8... per the corpus
# manifest) and the pinned extraction jsonl. No gold file is ever read by
# any compiler in this module — the poisoned-gold canary (design §2.1,
# PC-4) depends on that separation.

def load_exceptions(pos):
    exc = {}
    for line in open(DICT / ("verb.exc" if pos == "v" else "noun.exc")):
        f = line.split()
        if len(f) >= 2:
            exc.setdefault(f[0], f[1])
    return exc


def load_index(pos):
    """index.noun/index.verb: lemma -> ordered synset offsets (sense order)."""
    idx = {}
    for line in open(DICT / ("index.noun" if pos == "n" else "index.verb")):
        if line.startswith("  "):
            continue
        f = line.split()
        cnt = int(f[2])
        idx[f[0]] = f[-cnt:]
    return idx


def load_sense_tags():
    """index.sense: (lemma, pos_char) -> {offset: max tag_cnt} (SemCor)."""
    tags = {}
    for line in open(DICT / "index.sense"):
        f = line.split()
        key, off, snum, tag = f[0], f[1], int(f[2]), int(f[3])
        lemma, rest = key.split("%", 1)
        pos = {"1": "n", "2": "v"}.get(rest[0])
        if pos is None:
            continue
        d = tags.setdefault((lemma, pos), {})
        d[off] = max(d.get(off, 0), tag)
    return tags


def load_verb_frames():
    """data.verb: offset -> sorted frame numbers (w_num 00 = all words).
    Frame entries are the '+ ff ww' groups before the gloss bar."""
    frames = {}
    for line in open(DICT / "data.verb"):
        if line.startswith("  "):
            continue
        head = line.split("|")[0]
        off = head.split()[0]
        frames[off] = sorted({int(f) for f, w in re.findall(r"\+ (\d{2}) (\w{2})", head)})
    return frames


def load_frame_object_slots():
    """verb.Framestext: frame number -> object slot in {'somebody',
    'something', None}. Mechanical rule (ASM-1995): the object slot is the
    single token immediately following the '----s'/'----ing' verb slot,
    counted only when it is literally 'somebody' or 'something'."""
    slots = {}
    for line in open(DICT / "verb.Framestext"):
        f = line.split()
        if not f or not f[0].isdigit():
            continue
        num = int(f[0])
        toks = [t.lower().strip("'(),") for t in f[1:]]
        obj = None
        for i, t in enumerate(toks):
            if t.startswith("----"):
                if i + 1 < len(toks) and toks[i + 1] in ("somebody", "something"):
                    obj = toks[i + 1]
                break
        slots[num] = obj
    return slots


def load_noun_hypernyms():
    hyper = {}
    for line in open(ROOT / "data/lexical-wn31/synsets-noun.jsonl"):
        r = json.loads(line)
        hyper[r["id"]] = sorted(a["target"] for a in r["axioms"]
                                if a["rel"] in ("hypernym", "instanceHypernym"))
    return hyper


def load_synset_annotations(want):
    """{synset urn -> {'lemmas':[...], 'gloss': str}} for the wanted set."""
    out = {}
    for pos in ("verb", "noun"):
        for line in open(ROOT / ("data/lexical-wn31/synsets-%s.jsonl" % pos)):
            r = json.loads(line)
            if r["id"] in want:
                out[r["id"]] = r["annotations"]
    missing = sorted(set(want) - set(out))
    if missing:
        raise RuntimeError("synsets missing from pinned extraction: %s" % missing)
    return out


class WN:
    """One-shot loaded WN31 mechanical facts (pinned bytes only)."""

    def __init__(self):
        self.vexc = load_exceptions("v")
        self.nexc = load_exceptions("n")
        self.vidx = load_index("v")
        self.nidx = load_index("n")
        self.tags = load_sense_tags()
        self.frames = load_verb_frames()
        self.frame_obj = load_frame_object_slots()
        self.hyper = load_noun_hypernyms()
        self._closure_cache = {}

    # ---- morphology (WN morphy, minimal deterministic subset) ----
    def verb_bases(self, tok):
        out = set()
        if tok in self.vexc:
            out.add(self.vexc[tok])
        if tok in self.vidx:
            out.add(tok)
        for suf, rep in (("ies", "y"), ("es", "e"), ("es", ""), ("s", ""),
                         ("ied", "y"), ("ed", "e"), ("ed", ""),
                         ("ing", "e"), ("ing", "")):
            if tok.endswith(suf):
                cand = tok[: -len(suf)] + rep
                if cand in self.vidx:
                    out.add(cand)
        return out

    def noun_base(self, tok):
        if tok in self.nidx:
            return tok
        if tok in self.nexc and self.nexc[tok] in self.nidx:
            return self.nexc[tok]
        for suf, rep in (("ies", "y"), ("ses", "s"), ("xes", "x"),
                         ("zes", "z"), ("ches", "ch"), ("shes", "sh"),
                         ("es", ""), ("s", "")):
            if tok.endswith(suf):
                cand = tok[: -len(suf)] + rep
                if cand in self.nidx:
                    return cand
        return None

    # ---- noun -> synset -> top-split side ----
    def noun_synset(self, noun):
        """Most-SemCor-tagged sense; ties/zero-tag -> sense 1 (ASM-1992:
        third-party frequency-based sense selection, mechanical)."""
        offs = self.nidx.get(noun)
        if not offs:
            return None
        tagmap = self.tags.get((noun, "n"), {})
        best = max(offs, key=lambda o: (tagmap.get(o, 0), -offs.index(o)))
        return "urn:lexical-wn31:n-" + best

    def closure_hits(self, syn):
        if syn in self._closure_cache:
            return self._closure_cache[syn]
        seen, stack, hits = set(), [syn], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            if x in (PHYSICAL_ENTITY, ABSTRACTION, PERSON):
                hits.add(x)
            stack.extend(self.hyper.get(x, ()))
        self._closure_cache[syn] = hits
        return hits

    def noun_side(self, noun):
        """G2 side (design §2.1): WN hypernym closure to the top split.
        Returns 'phys' | 'abst' | None (None = undetermined, excluded)."""
        syn = self.noun_synset(noun)
        if syn is None:
            return None
        hits = self.closure_hits(syn)
        phys = PHYSICAL_ENTITY in hits
        abst = ABSTRACTION in hits
        if phys == abst:
            return None
        return "phys" if phys else "abst"

    def noun_is_person(self, noun):
        syn = self.noun_synset(noun)
        return syn is not None and PERSON in self.closure_hits(syn)

    def dominant_synset(self, lemma, pos):
        """SemCor-dominant sense of (lemma,pos) by tag_cnt; ties -> lowest
        sense number (design §1.3 D-word-dom row; ASM-1993)."""
        offs = (self.vidx if pos == "v" else self.nidx)[lemma]
        tagmap = self.tags.get((lemma, pos), {})
        best = max(offs, key=lambda o: (tagmap.get(o, 0), -offs.index(o)))
        return "urn:lexical-wn31:%s-%s" % (pos, best)


# ============================================================ item extraction
# Design §1.4: an item = one attested (or constructed-anomaly, or
# excluded-sense) occurrence of a Stage-A lemma with its argument noun.
# Everything below is mechanical over pinned bytes; every exclusion is
# logged with a named reason (PC-5 accounting, ASM-1991).

EXAMPLE_RE = re.compile(r'"([^"]+)"')


def kernel_inventory():
    """kernel-v1 Stage-A: minted synset->sense map + excluded synsets."""
    man = json.load(open(KV1 / "manifest.json"))
    minted = {}   # synset urn -> sense urn
    lemma_of_sense = {}
    for c in man["concepts"]:
        for s in c["wn31Synsets"]:
            minted[s] = c["id"]
        lemma_of_sense[c["id"]] = c["lemma"]
    excluded = {}  # synset urn -> lemma
    for lem in LEMMAS:
        si = json.load(open(KV1 / "sense-index" / ("%s.json" % lem)))
        for e in si["excludedSenses"]:
            excluded[e["synset"]] = lem
    return minted, excluded, lemma_of_sense


def _match_lemma_at(tokens, i, lemma_forms):
    """Longest multiword lemma match starting at token i; returns token count
    or 0. lemma_forms: {first_token_base: [(token_tuple), ...]}"""
    for forms in lemma_forms:
        n = len(forms)
        if i + n <= len(tokens) and tuple(tokens[i:i + n]) == forms:
            return n
    return 0


def parse_example(wn, sentence, lemmas):
    """Deterministic verb+object-NP parse (ASM-1991).

    Returns (verb_index, verb_len, object_noun, how) or (None, reason).
    how in {'object','subject'} — 'subject' = intransitive/passive fallback:
    the undergoer is the subject NP (design §1.5 W2 'the figurine broke')."""
    raw = [t for t in re.findall(r"[A-Za-z']+", sentence.lower())]
    toks = [t.strip("'") for t in raw if t.strip("'")]
    # verb match: any inflected form of any synset lemma (multiword via '_')
    vi = vlen = None
    for i, t in enumerate(toks):
        for lem in lemmas:
            parts = lem.lower().split("_")
            bases = wn.verb_bases(toks[i])
            if parts[0] in bases or toks[i] == parts[0]:
                if len(parts) == 1:
                    vi, vlen = i, 1
                    break
                if toks[i + 1:i + len(parts)] == parts[1:]:
                    vi, vlen = i, len(parts)
                    break
        if vi is not None:
            break
    if vi is None:
        # noun-lemma concepts (friend): match the noun itself as the predicate
        for i, t in enumerate(toks):
            base = wn.noun_base(t)
            if base in [l.lower() for l in lemmas]:
                vi, vlen = i, 1
                break
    if vi is None:
        return None, "no-lemma-match"

    def head_noun(span):
        content = []
        for t in span:
            if t in NP_STOP:
                break
            if t in PRONOUNS:
                # a pronoun ends/owns the NP: the undergoer is the pronoun's
                # referent, never a later noun ('made me buy a new sofa')
                return "PRONOUN" if not content else None
            content.append(t)
        while content and content[0] in DETERMINERS:
            content.pop(0)
        for j in range(len(content) - 1, -1, -1):
            t = content[j]
            if t in PRONOUNS or t in DETERMINERS:
                continue
            base = wn.noun_base(t)
            if base:
                return base
        if any(t in PRONOUNS for t in span[:2]):
            return "PRONOUN"
        return None

    obj = head_noun(toks[vi + vlen:])
    if obj == "PRONOUN":
        return None, "pronoun-argument"
    if obj is not None:
        return (vi, vlen, obj, "object"), None
    # intransitive / passive / clausal-complement -> subject NP fallback.
    # A pronoun ANYWHERE in the subject span voids the fallback (the
    # undergoer is the pronoun's referent, not a later modifier noun —
    # 'he was my best friend' must NOT yield head noun 'best'; ASM-1991).
    pre = [t for t in toks[:vi] if t not in AUX]
    if any(t in PRONOUNS for t in pre):
        return None, "pronoun-argument"
    subj = head_noun(pre) if pre else None
    if subj not in (None, "PRONOUN"):
        return (vi, vlen, subj, "subject"), None
    if obj == "PRONOUN" or subj == "PRONOUN":
        return None, "pronoun-argument"
    return None, "no-nominal-argument"


def extract_items(wn):
    """The mechanical item extractor (design §1.4-§1.5; ASM-1991/1992).

    Item kinds:
      attested   G1xG2 gold: verdict CONSISTENT (attested third-party usage)
      anomaly    G3 constructed cross-pair: verdict ANOMALOUS
      refusal    G4 excluded-sense occurrence: verdict REFUSE (scoring rule
                 ASM-1997: REFUSE or vacuous CONSISTENT correct; ANOMALOUS
                 = confident wrong assertion, incorrect)
    Returns (items, gold, exclusions, attested_sides).
    """
    minted, excluded, _ = kernel_inventory()
    want = sorted(set(minted) | set(excluded))
    ann = load_synset_annotations(want)
    items, gold, exclusions = [], {}, []
    attested = {}   # synset -> {'objects': {noun: side}, 'lemma': str}

    def synset_lemma(s):
        if s in excluded:
            return excluded[s]
        sense = minted[s]
        return sense.split(":")[-1].split(".")[0]

    candidates = 0
    for s in want:
        a = ann[s]
        lemma = synset_lemma(s)
        for ei, ex in enumerate(EXAMPLE_RE.findall(a["gloss"])):
            parsed, reason = parse_example(wn, ex, a["lemmas"])
            if parsed is None:
                exclusions.append({"synset": s, "example": ex, "reason": reason})
                continue
            _, _, noun, how = parsed
            candidates += 1
            side = wn.noun_side(noun)
            if side is None:
                exclusions.append({"synset": s, "example": ex,
                                   "reason": "side-undetermined:%s" % noun})
                continue
            kind = "attested" if s in minted else "refusal"
            iid = "ei-%s-%s-%s-%02d" % (lemma, kind, s.split("-")[-1], ei)
            items.append({
                "id": iid, "kind": kind, "lemma": lemma,
                "gold_synset": s, "object_noun": noun, "object_side": side,
                "arg_slot": how, "source_example": ex,
                "sense": minted.get(s)})
            gold[iid] = {"verdict": "CONSISTENT" if s in minted else "REFUSE",
                         "sense": minted.get(s), "object_side": side,
                         "gold_rule": "G1+G2" if s in minted else "G4"}
            if s in minted:
                attested.setdefault(s, {"lemma": lemma, "objects": {}})
                attested[s]["objects"].setdefault(noun, side)

    # ---- constructed cross-pair anomalies (G3, design §2.1 rule) ----
    # ANOMALOUS iff the verb-sense's UNANIMOUS attested example-object side
    # and the item's object side fall on opposite top-split sides. Senses
    # with mixed/absent attested sides are skipped (logged) — the G3 rule is
    # only defined where the attested side is unambiguous (ASM-1992).
    unanimous = {}
    for s, rec in sorted(attested.items()):
        sides = sorted(set(rec["objects"].values()))
        if len(sides) == 1:
            unanimous[s] = sides[0]
        else:
            exclusions.append({"synset": s, "reason": "g3-mixed-attested-sides",
                               "sides": sides})
    for s, s_side in sorted(unanimous.items()):
        lemma = synset_lemma(s)
        for s2, s2_side in sorted(unanimous.items()):
            if s2 == s or synset_lemma(s2) != lemma or s2_side == s_side:
                continue
            for noun, n_side in sorted(attested[s2]["objects"].items()):
                if n_side == s_side:
                    continue
                iid = "ei-%s-anomaly-%s-x-%s" % (lemma, s.split("-")[-1], noun)
                items.append({
                    "id": iid, "kind": "anomaly", "lemma": lemma,
                    "gold_synset": s, "object_noun": noun,
                    "object_side": n_side, "arg_slot": "object",
                    "source_example": "cross-pair: %s object of %s" % (noun, s2),
                    "sense": kernel_inventory()[0].get(s)})
                gold[iid] = {"verdict": "ANOMALOUS", "sense": None,
                             "object_side": n_side, "gold_rule": "G3"}

    items.sort(key=lambda it: it["id"])
    stats = {"candidate_occurrences": candidates,
             "well_formed": sum(1 for i in items if i["kind"] != "anomaly"),
             "yield_rate": (sum(1 for i in items if i["kind"] != "anomaly")
                            / candidates if candidates else 0.0)}
    return items, gold, exclusions, stats


# ================================================================ arm sources
# Design §1.3. All arms share: engine bytes, world compiler, scorer, item
# bank, and the shared class vocabulary module (data/axioms-engineinf-v0/
# classes/). They differ ONLY in the relation-typing module + the sense
# projection that DEFINES each source (word-level sources cannot consume the
# sense tag — the rules-2-knull comparator construction).

def axiom_record(subject, constraints, note):
    return {"schema": "kot-axiom/1", "subject": subject,
            "constraints": constraints, "note": note}


def build_dword_arms(wn, out_dir):
    """D-word-dom / D-word-union (plain word-level dictionary; design §1.3).

    One relation per (lemma, kernel pos). D-word-dom's signature is the
    SemCor-dominant sense's signature, derived mechanically with NO kernel
    authoring: the majority G2 side of the dominant synset's OWN parsed
    gloss-example objects (ASM-1993); ties/none -> untyped. D-word-union is
    the union/least-common-subsumer signature = untyped (design §1.3)."""
    want = set()
    minted, excluded, _ = kernel_inventory()
    ann = load_synset_annotations(sorted(set(minted) | set(excluded)))
    dom, uni = [], []
    dom_meta = {}
    for lemma in LEMMAS:
        pos = LEMMA_POS[lemma]
        rel = "urn:kot-engineinf:dword:%s" % lemma
        dsyn = wn.dominant_synset(lemma, pos)
        sides = []
        if dsyn in ann:
            for ex in EXAMPLE_RE.findall(ann[dsyn]["gloss"]):
                parsed, _ = parse_example(wn, ex, ann[dsyn]["lemmas"])
                if parsed:
                    side = wn.noun_side(parsed[2])
                    if side:
                        sides.append(side)
        else:
            # dominant sense outside the Stage-A synset set: parse its gloss
            # from the pinned extraction on demand
            ann2 = load_synset_annotations([dsyn])
            for ex in EXAMPLE_RE.findall(ann2[dsyn]["gloss"]):
                parsed, _ = parse_example(wn, ex, ann2[dsyn]["lemmas"])
                if parsed:
                    side = wn.noun_side(parsed[2])
                    if side:
                        sides.append(side)
        n_p, n_a = sides.count("phys"), sides.count("abst")
        target = None
        if n_p != n_a and sides:
            target = C["phys"] if n_p > n_a else C["abst"]
        cons = [{"kind": "classDeclaration"}]
        if target:
            cons = [{"kind": "range", "target": target}]
        dom.append(axiom_record(
            rel, cons,
            "D-word-dom %s: SemCor-dominant synset %s (index.sense tag_cnt); "
            "signature = majority G2 side of its own gloss-example objects "
            "(%d phys / %d abst) -> %s. Mechanical, zero kernel authoring "
            "(design §1.3; ASM-1993)." % (lemma, dsyn, n_p, n_a, target)))
        uni.append(axiom_record(
            rel, [{"kind": "classDeclaration"}],
            "D-word-union %s: union/LCS signature over all senses = "
            "effectively untyped (design §1.3)." % lemma))
        dom_meta[lemma] = {"dominant_synset": dsyn, "sides": sides,
                           "range": target}
    _write_module(out_dir / "dword-dom", dom)
    _write_module(out_dir / "dword-union", uni)
    return dom_meta


def build_bwn_arm(wn, out_dir):
    """B-wn (the kernel-specificity decider, design §1.3 + ASM-1956):
    WordNet 3.1 bytes only, zero kernel authoring. One relation per synset
    (same sense identity kernel-v1 keys on, disclosed); typing = the verb
    sentence-frame object slot (Somebody/Something), mechanically parsed
    from the pinned data.verb + verb.Framestext (ASM-1995). Noun-lemma
    synsets (friend) have no frames -> untyped."""
    minted, excluded, _ = kernel_inventory()
    recs, meta = [], {}
    for s in sorted(set(minted) | set(excluded)):
        rel = "urn:kot-engineinf:bwn:%s" % s.split(":")[-1]
        target = None
        if s.split(":")[-1].startswith("v-"):
            off = s.split("-")[-1]
            slots = {wn.frame_obj.get(f) for f in wn.frames.get(off, [])}
            slots.discard(None)
            if slots == {"somebody"}:
                target = C["wn-somebody"]
            elif slots == {"something"}:
                target = C["wn-something"]
        cons = ([{"kind": "range", "target": target}] if target
                else [{"kind": "classDeclaration"}])
        recs.append(axiom_record(
            rel, cons,
            "B-wn %s: object slot from WN sentence frames (mechanical; "
            "frames consume ONLY the frame field — the provenance-separation "
            "rule §2.1/ASM-1957 keeps gold on hypernym+example fields)." % s))
        meta[s] = target
    _write_module(out_dir / "bwn", recs)
    return meta


def build_kshuf_arm(out_dir):
    """K-shuf (mandatory shuffled-kernel control, design §4.1): derange the
    per-sense domain/range constraint sets ACROSS senses within lemma —
    fixed rotation by 1 over URN-sorted senses (deterministic; ASM-1996).
    Byte bulk identical: subPropertyOf/classDeclaration constraints stay."""
    kdir = MODULE / "kernel"
    senses = {}
    for p in sorted(kdir.glob("sense-*.json")):
        rec = json.loads(p.read_text())
        senses[rec["subject"]] = rec
    by_lemma = {}
    for urn in sorted(senses):
        lemma = urn.split(":")[-1].split(".")[0]
        by_lemma.setdefault(lemma, []).append(urn)
    recs = []
    for lemma, urns in sorted(by_lemma.items()):
        moved = {u: [c for c in senses[u]["constraints"]
                     if c["kind"] in ("domain", "range")] for u in urns}
        for i, u in enumerate(urns):
            donor = urns[(i - 1) % len(urns)]
            kept = [c for c in senses[u]["constraints"]
                    if c["kind"] not in ("domain", "range")]
            recs.append(axiom_record(
                u, kept + moved[donor],
                "K-shuf: domain/range deranged within lemma %s — this sense "
                "carries %s's typing (rotation by 1 over URN order; "
                "ASM-1996). Control prediction: false conflicts on attested "
                "items + missed anomalies (PC-3)." % (lemma, donor)))
    _write_module(out_dir / "kshuf", recs)


def _write_module(d, recs):
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.json"):
        old.unlink()
    for rec in recs:
        name = re.sub(r"[^a-z0-9.-]+", "-", rec["subject"].split(":")[-1].lower())
        (d / ("%s.json" % name)).write_text(
            json.dumps(rec, indent=1, sort_keys=True) + "\n")


ARM_NAMES = ("K", "K-shuf", "D-word-dom", "D-word-union", "B-wn")


def arm_tbox_paths(arms_dir):
    classes = MODULE / "classes"
    return {
        "K": [classes, MODULE / "kernel"],
        "K-shuf": [classes, arms_dir / "kshuf"],
        "D-word-dom": [classes, arms_dir / "dword-dom"],
        "D-word-union": [classes, arms_dir / "dword-union"],
        "B-wn": [classes, arms_dir / "bwn"],
    }


def arm_relation(arm, item, minted):
    """The source-side sense projection (design §1.4, grade S): K and B-wn
    map the third-party gold synset mechanically (K -> NONE on excluded
    senses = fail-closed refusal); D-word arms CANNOT consume the tag and
    collapse to the lemma relation (the matched word-level comparison)."""
    s = item["gold_synset"]
    if arm in ("K", "K-shuf"):
        sense = minted.get(s)
        return "urn:%s" % sense.split("urn:")[-1] if sense else None
    if arm == "B-wn":
        return "urn:kot-engineinf:bwn:%s" % s.split(":")[-1]
    return "urn:kot-engineinf:dword:%s" % item["lemma"]


# ============================================================= world compiler
# Shared byte-identically by all arms (design §1.1): stated flat cls facts
# precomputed mechanically from pinned WN31 hypernym axioms (no cax-sco in
# the certified inventory). The relation URN is a per-arm substitution into
# the SAME arm-neutral world (ASM-1998: the undergoer-slot convention —
# rel(anchor, R, undergoer); intransitive occurrences put the subject NP in
# the undergoer slot; the anchor entity carries no class facts).

def neutral_world(wn, item):
    u = "urn:kot-engineinf:e:%s:u" % item["id"]
    a = "urn:kot-engineinf:e:%s:a" % item["id"]
    side_cls = C["phys"] if item["object_side"] == "phys" else C["abst"]
    wn_cls = C["wn-somebody"] if wn.noun_is_person(item["object_noun"]) \
        else C["wn-something"]
    return {"anchor": a, "undergoer": u,
            "stated": [["rel", a, "@REL@", u],
                       ["cls", u, side_cls],
                       ["cls", u, wn_cls]]}


def run_item(tbox, world, rel):
    """One engine decision. Returns (verdict, refusal_code, derived_cls)."""
    if rel is None:
        # fail-closed: the arm's source has no relation for this sense
        # (design §1.1 O3; twin_engine ERR_INSUFFICIENT_PREMISES semantics)
        return "REFUSE", "ERR_INSUFFICIENT_PREMISES", []
    stated = [tuple(f[:2] + [rel] + f[3:]) if f[2] == "@REL@" else tuple(f)
              for f in world["stated"]]
    try:
        cl = Closure(tbox, stated)
    except EngineError as e:
        return "REFUSE", e.code, []
    derived = sorted(f[2] for f in cl.derived()
                     if f[0] == "cls" and f[1] == world["undergoer"])
    if cl.conflicts:
        return "ANOMALOUS", "ERR_CONFLICT", derived
    return "CONSISTENT", None, derived


def derived_sides(derived_cls):
    return sorted({SIDES[c] for c in derived_cls if SIDES.get(c)})


# ==================================================================== scoring
# Design §2.2 + ASM-1997, refined by ASM-2116 (R2, 2026-07-13):
#   gold CONSISTENT: correct iff verdict CONSISTENT
#   gold ANOMALOUS : correct iff verdict ANOMALOUS
#   gold REFUSE    : correct iff verdict REFUSE (the covered-elsewhere arm's
#                    honest answer) OR verdict CONSISTENT *with an EMPTY
#                    derived-class set* (true vacuity: the arm asserted
#                    nothing). CONSISTENT *carrying a derived class* is a
#                    confident wrong assertion (the §1.5 W3 case), and so is
#                    ANOMALOUS on an attested third-party usage = incorrect.
# derived_cls defaults to empty so the oracle callsites (which inject the
# gold verdict) and the mock validator (verdict-axis only) are unaffected:
# a G4 oracle row is REFUSE with empty derived and stays correct (PC-5).
# Honesty-weighted penalty (issue-#18 direction, fixed at freeze):
#   correct 0; refusal where gold != REFUSE 0.5; any other wrong 1.0.

def score(gold_rec, verdict, derived_cls=None):
    derived_cls = derived_cls or []
    g = gold_rec["verdict"]
    if g == "REFUSE":
        correct = verdict == "REFUSE" or (
            verdict == "CONSISTENT" and not derived_cls)
    else:
        correct = verdict == g
    if correct:
        pen = 0.0
    elif verdict == "REFUSE":
        pen = 0.5
    else:
        pen = 1.0
    return correct, pen


def row_signature(row):
    """Full divergence signature (design §2.3 'verdict-or-derived-fact
    set'): verdict + refusal code + G2-side projection of derived undergoer
    classes (ASM-1994 — decision-relevant divergence, not URN trivia)."""
    return (row["verdict"], row["refusal"] or "", tuple(row["derived_sides"]))


def divergence(rows_by_arm, baseline, items_by_id):
    """Div(K, b) certificates: full-signature and decision-level (verdict)."""
    full, dec = [], []
    for iid in sorted(rows_by_arm["K"]):
        k, b = rows_by_arm["K"][iid], rows_by_arm[baseline][iid]
        if row_signature(k) != row_signature(b):
            full.append(iid)
        if (k["verdict"], k["refusal"]) != (b["verdict"], b["refusal"]):
            dec.append(iid)
    def ops(iid):
        k, b = rows_by_arm["K"][iid], rows_by_arm[baseline][iid]
        o = []
        if tuple(k["derived_sides"]) != tuple(b["derived_sides"]):
            o.append("O1")
        if (k["verdict"] == "ANOMALOUS") != (b["verdict"] == "ANOMALOUS"):
            o.append("O2")
        if (k["verdict"] == "REFUSE") != (b["verdict"] == "REFUSE"):
            o.append("O3")
        return o
    comp = {"per_op": {}, "per_lemma": {}}
    for iid in full:
        for o in ops(iid):
            comp["per_op"][o] = comp["per_op"].get(o, 0) + 1
        lem = items_by_id[iid]["lemma"]
        comp["per_lemma"][lem] = comp["per_lemma"].get(lem, 0) + 1
    return {"baseline": baseline, "full": full, "decision": dec,
            "composition": comp}
