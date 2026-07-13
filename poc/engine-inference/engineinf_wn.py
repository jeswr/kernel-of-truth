#!/usr/bin/env python3
# ENGINE-INF engine-free core: pinned-WN31 parsing, the kernel-v1 sense
# inventory, the mechanical item extractor, and the outcome-equivalence
# cell key.
#
# WHY THIS FILE EXISTS (custody, design §2.5 [R1] / ASM-2104): the
# confirmatory-holdout extractor must be "a separate entrypoint that does
# not import the engine or scorer". The original engineinf_lib.py imported
# poc/rules-1/twin_engine.py at module load, so nothing that imported it
# could satisfy that custody clause mechanically. This module carries the
# byte-identical WN/parsing/extraction code MOVED (not re-authored) out of
# engineinf_lib.py; it imports NO engine and defines NO scorer.
# engineinf_lib.py re-exports everything here, so all engine-side callsites
# are unchanged.
#
# Design anchors as before: docs/next/design/engine-inference-under-typing.md
# §1.4-§1.5, §2.1, §2.2 [R1] (the cell key); ASM-1991/1992 (extractor rules),
# ASM-2106 (outcome-equivalence cell as the inference unit).
#
# Determinism: no wall-clock, no RNG; all iteration over sorted structures;
# fail-closed (unknown cases raise or are logged exclusions).

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DICT = ROOT / "data/lexical-wn31/source/dict"
KV1 = ROOT / "data/kernel-v1"
MODULE = ROOT / "data/axioms-engineinf-v0"
SEMCOR = ROOT / "data/semcor30"

LEMMAS = ("break", "find", "friend", "make")          # Stage-A inventory (ASM-1951)
LEMMA_POS = {"break": "v", "find": "v", "friend": "n", "make": "v"}

# PC-6 decoy lemmas (design §2.5/§5 PC-6, ASM-2111): members of neither
# Stage-A nor the kernel-v0 39-concept panel (verified mechanically in the
# pilot); their outcomes are quarantined and touch no endpoint.
DECOY_LEMMAS = ("cut", "draw", "hold")
DECOY_POS = {"cut": "v", "draw": "v", "hold": "v"}

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


def load_sense_keys(lemmas):
    """index.sense: full sense-key -> (pos_char, offset) map for the given
    lemmas (holdout extractor: SemCor lexsn keys are version-stable and map
    to WN3.1 offsets through this pinned file; unmappable keys are logged
    exclusions — design §2.5 H1 [R1])."""
    want = set(lemmas)
    keys = {}
    for line in open(DICT / "index.sense"):
        f = line.split()
        key, off = f[0], f[1]
        lemma, rest = key.split("%", 1)
        if lemma not in want:
            continue
        pos = {"1": "n", "2": "v"}.get(rest[0])
        if pos is None:
            continue
        keys[key] = (pos, off)
    return keys


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


# =============================================== outcome-equivalence cell key
# Design §2.2 [R1], ASM-2106 verbatim: the cell is the tuple (gold sense
# synset, undergoer top-split side class, undergoer wn-kind class, item
# kind) — the full arm-input equivalence class up to entity renaming. All
# registered inference is at CELL level; the novel-cell holdout restriction
# H* (§2.5) and the C-SHUF A_union frame (§2.3 [R3]) are cell-keyed.

def wn_kind_cls(wn, noun):
    return C["wn-somebody"] if wn.noun_is_person(noun) else C["wn-something"]


def cell_key(wn, item):
    return (item["gold_synset"], item["object_side"],
            wn_kind_cls(wn, item["object_noun"]), item["kind"])


def cell_key_str(key):
    return "|".join(key)


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
                 ASM-1997/2116: REFUSE or truly-vacuous CONSISTENT correct;
                 a confident derived assertion = incorrect)
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
