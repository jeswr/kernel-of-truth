#!/usr/bin/env python3
# ENGINE-INF (D2/D3) shared library — divergence-seam construction over the
# certified RULES-1 engine.
#
# Design anchors (every mechanical rule cites its source):
#   docs/next/design/engine-inference-under-typing.md (the DESIGN through
#   REVISION-3; §1 divergence-seam construction, §1.3 arms + §1.3.1 the
#   lemma-collapse rules [R1], §1.4 items/input grade S, §2 deterministic
#   gold G1-G4 + scoring [R2 G4 rule], §2.3 divergence certificate +
#   co-primary endpoints + C-SHUF orbit gate [R2/R3], §4.1 the 960-member
#   within-lemma permutation orbit, §5 blocking pilot PC-1..PC-7)
#   docs/next/protocol/blocking-pilot-before-freeze.md (kot-pilot/1 contract)
#   ASM-1950..1967 (design) + ASM-1990..2009 (build operationalisations) +
#   ASM-2100..2112 (REVISION-1) + ASM-2113..2117 (REVISION-2) +
#   ASM-2120..2121 (REVISION-3).
#
# Engine identity: poc/rules-1/twin_engine.py, UNCHANGED (design §1.1 —
# "no new rule kind, no engine version change" at E0). This library only
# COMPILES inputs for it and READS its closure.
#
# Module split (custody, §2.5 [R1]/ASM-2104): all engine-free WN parsing /
# item extraction / cell-key code lives in engineinf_wn.py (byte-moved, not
# re-authored) so the holdout extractor can run WITHOUT importing the engine
# or the scorer. This module re-exports those names for existing callsites.
#
# Determinism: no wall-clock, no RNG anywhere; all iteration over sorted
# structures; the C-SHUF control is the EXHAUSTIVE 960-member orbit
# (ASM-2114; the single-rotation K-shuf arm of ASM-1996 is RETIRED).
# Fail-closed: unknown/underivable cases raise or are logged exclusions —
# never silently defaulted.

import itertools
import json
import re
import sys
from pathlib import Path

from engineinf_wn import (  # noqa: F401  (re-exports for existing callsites)
    ROOT, DICT, KV1, MODULE, SEMCOR, LEMMAS, LEMMA_POS, DECOY_LEMMAS,
    DECOY_POS, C, SIDES, PHYSICAL_ENTITY, ABSTRACTION, PERSON, PRONOUNS,
    DETERMINERS, NP_STOP, AUX, sha256_file, canon_sha, load_exceptions,
    load_index, load_sense_tags, load_sense_keys, load_verb_frames,
    load_frame_object_slots, load_noun_hypernyms, load_synset_annotations,
    WN, wn_kind_cls, cell_key, cell_key_str, EXAMPLE_RE, kernel_inventory,
    parse_example, extract_items)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "poc" / "rules-1"))
from twin_engine import Closure, EngineError, TBox, load_tbox  # noqa: E402  (pinned engine)


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
    binomial proportion, by bisection on the exact tail (deterministic).
    NOTE [R2/ASM-2115]: no longer part of any registered PASS gate (the
    exact-census rules replaced all interval gates); retained for the mock
    validator and descriptive readouts only."""
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


# ================================================================ arm sources
# Design §1.3 [R1]. All arms share: engine bytes, world compiler, scorer,
# item bank, the shared class vocabulary module (data/axioms-engineinf-v0/
# classes/), AND the same compiler input record per item including the gold
# sense tag (ASM-2101). They differ ONLY in the source module compiled into
# the TBox and in whether that module's relation inventory is per-sense or
# per-lemma (a per-lemma inventory is constitutively constant in the tag —
# verified by the PC-4' sense-tag insensitivity canary).

def axiom_record(subject, constraints, note):
    return {"schema": "kot-axiom/1", "subject": subject,
            "constraints": constraints, "note": note}


def build_dword_arms(wn, out_dir):
    """D-word-dom / D-word-union (plain word-level dictionary; design §1.3).

    One relation per (lemma, kernel pos). D-word-dom's signature is the
    SemCor-dominant sense's signature, derived mechanically with NO kernel
    authoring: the majority G2 side of the dominant synset's OWN parsed
    gloss-example objects (ASM-1993); ties/none -> untyped. D-word-union is
    the union/least-common-subsumer signature = untyped (design §1.3).
    [R1] Both arms are DESCRIPTIVE CONTEXT only (ASM-2102): they confound
    source and split and license nothing."""
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
    """B-wn (the kernel-source decider, design §1.3 + ASM-1956/2102):
    WordNet 3.1 bytes only, zero kernel authoring. One relation per synset
    (same sense identity kernel-v1 keys on, disclosed); typing = the verb
    sentence-frame object slot (Somebody/Something), mechanically parsed
    from the pinned data.verb + verb.Framestext (ASM-1995). Noun-lemma
    synsets (friend) have no frames -> untyped."""
    minted, excluded, _ = kernel_inventory()
    recs = bwn_frame_records(wn, sorted(set(minted) | set(excluded)))
    _write_module(out_dir / "bwn", recs)
    return {r["subject"]: ([c["target"] for c in r["constraints"]
                            if c["kind"] == "range"] or [None])[0]
            for r in recs}


def bwn_frame_records(wn, synsets):
    """The B-wn mechanical frame-typing rule (ASM-1995) over an explicit
    synset list — shared by the real B-wn arm build and the PC-6 decoy
    pipeline (same code path, so the decoys exercise the real rule)."""
    recs = []
    for s in sorted(synsets):
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
    return recs


# ---- the matched sense-split-isolating pair (design §1.3.1 [R1], ASM-2101) --

def _kernel_sense_records():
    """{sense urn -> pinned record} from data/axioms-engineinf-v0/kernel/."""
    recs = {}
    for p in sorted((MODULE / "kernel").glob("sense-*.json")):
        rec = json.loads(p.read_text())
        recs[rec["subject"]] = rec
    return recs


def _dr(rec):
    """The domain/range constraint set of a pinned sense record."""
    return [c for c in rec["constraints"] if c["kind"] in ("domain", "range")]


def lemma_sense_urns():
    """URN-sorted minted sense URNs per lemma, from the pinned module bytes
    (MEASURED at build: break 5, find 2, friend 2, make 2)."""
    by_lemma = {}
    for urn in sorted(_kernel_sense_records()):
        lemma = urn.split(":")[-1].split(".")[0]
        by_lemma.setdefault(lemma, []).append(urn)
    return {l: sorted(us) for l, us in sorted(by_lemma.items())}


def klemma_dominants(wn):
    """The pinned dominant-minted-sense rule (ASM-2101): dominance = max
    summed pinned index.sense tag_cnt over the concept's wn31Synsets; ties
    break to the lexicographically smallest concept URN. The identical
    third-party ranking rule D-word-dom uses (ASM-1993) — no new source."""
    man = json.load(open(KV1 / "manifest.json"))
    out = {}
    for lemma in LEMMAS:
        concepts = [c for c in man["concepts"] if c["lemma"] == lemma]

        def tagsum(c):
            t = 0
            for s in c["wn31Synsets"]:
                tail = s.split(":")[-1]           # e.g. v-00364717
                pos, off = tail.split("-", 1)
                t += wn.tags.get((lemma, pos), {}).get(off, 0)
            return t

        best = sorted(concepts, key=lambda c: (-tagsum(c), c["id"]))[0]
        out[lemma] = {"concept": best["id"], "tag_sum": tagsum(best),
                      "all_tag_sums": {c["id"]: tagsum(c) for c in concepts}}
    return out


def build_klemma_arms(wn, out_dir):
    """K-lemma-dom / K-lemma-union — the matched sense-split isolators
    (design §1.3.1 [R1], ASM-2101; the B1 fix). Compiled from the SAME
    pinned data/axioms-engineinf-v0/kernel constraint sets by pinned
    mechanical collapse rules — no new authoring act anywhere:

      K-lemma-dom:   the lemma relation's domain/range constraint set :=
                     that of the lemma's DOMINANT minted sense
                     (klemma_dominants rule above).
      K-lemma-union: a domain (resp. range) constraint survives iff EVERY
                     minted sense of the lemma carries the identical
                     constraint class on that slot; otherwise the slot is
                     unconstrained (in the flat bridge-class vocabulary
                     agreement-or-nothing IS the LCS rule).

    Everything else byte-shared: classDeclarations and disjointness pairs
    come from the shared classes/ dir; the any-<lemma> coarse relations are
    inherited as byte-identical copies; only the per-sense relation axioms
    are replaced by ONE per-lemma relation each. The collapsed relation
    covers every occurrence of the lemma including excluded senses (a
    lemma-level source cannot mark coverage — that is part of what
    sense-splitting is; EP-A is restricted to G1∪G3 cells for exactly this
    reason, ASM-2101)."""
    senses = _kernel_sense_records()
    inv = lemma_sense_urns()
    dominants = klemma_dominants(wn)
    meta = {"dominants": dominants, "union_survivors": {}}
    for variant in ("dom", "union"):
        d = out_dir / ("klemma-%s" % variant)
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.json"):
            old.unlink()
        # inherited byte-identical: the any-<lemma> coarse relations
        for p in sorted((MODULE / "kernel").glob("any-*.json")):
            (d / p.name).write_bytes(p.read_bytes())
        for lemma in LEMMAS:
            urns = inv[lemma]
            if variant == "dom":
                src = dominants[lemma]["concept"]
                moved = _dr(senses[src])
                note = ("K-lemma-dom %s: ONE relation per lemma; domain/"
                        "range constraint set := that of the dominant "
                        "minted sense %s (max summed index.sense tag_cnt "
                        "over wn31Synsets, ties to smallest URN — the "
                        "ASM-1993 rule; ASM-2101 [R1]). Same pinned kernel "
                        "content as K, minus the split." % (lemma, src))
            else:
                moved = []
                for slot in ("domain", "range"):
                    targets = []
                    for u in urns:
                        ts = [c["target"] for c in _dr(senses[u])
                              if c["kind"] == slot]
                        targets.append(ts[0] if ts else None)
                    if len(set(targets)) == 1 and targets[0] is not None:
                        moved.append({"kind": slot, "target": targets[0]})
                meta["union_survivors"].setdefault(lemma, [
                    "%s=%s" % (c["kind"], c["target"]) for c in moved])
                note = ("K-lemma-union %s: ONE relation per lemma; a slot "
                        "constraint survives iff ALL minted senses carry "
                        "the identical constraint class on that slot "
                        "(agreement-or-nothing = LCS in the flat bridge "
                        "vocabulary; ASM-2101 [R1])." % lemma)
            rel = "urn:kot-engineinf:klem%s:%s" % (
                "dom" if variant == "dom" else "un", lemma)
            rec = axiom_record(
                rel,
                [{"kind": "subPropertyOf",
                  "target": "urn:kot-engineinf:any:%s" % lemma}] + moved,
                note)
            (d / ("klem%s-%s.json" % (variant, lemma))).write_text(
                json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return meta


# ---- the C-SHUF within-lemma permutation ORBIT (design §4.1 [R2], ASM-2114) --
# The single-rotation K-shuf ARM (ASM-1996) is RETIRED. The control is the
# COMPLETE orbit S5 x S2 x S2 x S2 = 960 relabelings of the per-sense
# domain/range constraint sets, identity and all fixed-point/tie members
# included — a control-evaluation set, not an arm. Member semantics: sense
# at URN-order index i receives the constraint set of sense at index
# perm[i] within the same lemma; subPropertyOf links and classDeclarations
# untouched; byte bulk preserved.

def orbit_members():
    """Canonical deterministic enumeration: per-lemma permutations in
    itertools lexicographic order (identity first), lemmas alphabetical,
    itertools.product order. Member 0 is the identity (= K)."""
    inv = lemma_sense_urns()
    lemmas = sorted(inv)
    per = [list(itertools.permutations(range(len(inv[l])))) for l in lemmas]
    return [{lemmas[i]: combo[i] for i in range(len(lemmas))}
            for combo in itertools.product(*per)]


def orbit_sense_records(member, senses=None, inv=None):
    """The permuted per-sense records for one orbit member (constraint
    content only; notes carry the assignment for auditability)."""
    senses = senses or _kernel_sense_records()
    inv = inv or lemma_sense_urns()
    recs = []
    for lemma in sorted(inv):
        urns = inv[lemma]
        perm = member[lemma]
        for i, u in enumerate(urns):
            donor = urns[perm[i]]
            kept = [c for c in senses[u]["constraints"]
                    if c["kind"] not in ("domain", "range")]
            recs.append(axiom_record(
                u, kept + _dr(senses[donor]),
                "C-SHUF orbit member: within-lemma relabeling, %s carries "
                "%s's domain/range set (ASM-2114)." % (u, donor)))
    return recs


def orbit_semantic_sha(records):
    """Canonical constraint-content sha (notes stripped) — used for the
    identity-reproduces-K check and the distinct-TBox count."""
    return canon_sha({r["subject"]: sorted(
        json.dumps(c, sort_keys=True) for c in r["constraints"])
        for r in records})


def _class_and_any_records():
    recs = []
    for d in (MODULE / "classes", MODULE / "kernel"):
        for p in sorted(d.glob("*.json")):
            if p.name == "manifest.json" or p.name.startswith("sense-"):
                continue
            recs.append(json.loads(p.read_text()))
    return recs


class OrbitEvaluator:
    """Evaluates every orbit member's engine decision on a cell frame.

    Cells within an outcome-equivalence class produce byte-identical worlds
    up to entity renaming (ASM-2106), so one representative item per cell is
    sufficient and exact. TBoxes are cached by semantic sha (ties: e.g.
    break's three identical 'range material' sets make many members
    functionally identical — correctly kept inside the orbit as tie members,
    §4.1)."""

    def __init__(self, wn, minted):
        self.wn = wn
        self.minted = minted
        self.senses = _kernel_sense_records()
        self.inv = lemma_sense_urns()
        self.base = _class_and_any_records()
        self.members = orbit_members()
        self._tbox_cache = {}
        self._result_cache = {}

    def member_records(self, m):
        return orbit_sense_records(self.members[m], self.senses, self.inv)

    def _tbox_for(self, m):
        recs = self.member_records(m)
        key = orbit_semantic_sha(recs)
        if key not in self._tbox_cache:
            tbox = TBox()
            for rec in self.base + recs:
                tbox.load_record(rec, "orbit:%s" % key[:12])
            self._tbox_cache[key] = tbox
        return key, self._tbox_cache[key]

    def eval_cells(self, cells):
        """cells: [{'cell': str, 'rep': item, 'gold_verdict': str}, ...] ->
        {m: {cell: row}} rows carry verdict/refusal/derived_sides."""
        out = {}
        for m in range(len(self.members)):
            key, tbox = self._tbox_for(m)
            ck_all = (key, canon_sha([c["cell"] for c in cells]))
            if ck_all in self._result_cache:
                out[m] = self._result_cache[ck_all]
                continue
            rows = {}
            for c in cells:
                it = c["rep"]
                world = neutral_world(self.wn, it)
                rel = arm_relation("K", it, self.minted)
                v, r, d = run_item(tbox, world, rel)
                rows[c["cell"]] = {"verdict": v, "refusal": r,
                                   "derived_sides": derived_sides(d)}
            self._result_cache[ck_all] = rows
            out[m] = rows
        return out


def cshuf_analysis(orbit_rows, gold_verdict_of_cell):
    """The R3-calibrated C-SHUF statistic (design §2.3 [R3], ASM-2120).

    orbit_rows: {m: {cell: {'verdict':..,'derived_sides':..}}} over ONE
    fixed candidate cell frame (the (G1∪G3) frame in force).
    Active(pi) = cells with non-empty derived_sides OR verdict ANOMALOUS.
    A_union = union over ALL members (orbit-invariant, identity included).
    T(pi) = correctness fraction over A_union (constant denominator).
    p = #{pi : T(pi) >= T(identity)} / |Orbit|  (ties in >=, conservative).
    """
    members = sorted(orbit_rows)
    a_union = sorted({cell for m in members
                      for cell, r in orbit_rows[m].items()
                      if r["derived_sides"] or r["verdict"] == "ANOMALOUS"})
    if not a_union:
        return {"a_union": [], "cshuf_active_n": 0, "cshuf_orbit_p": None,
                "cshuf_rank": None, "t_identity": None,
                "note": "A_union empty -> C-SHUF N/A (KILL-e2a upstream)"}
    t = {}
    for m in members:
        corr = sum(1 for cell in a_union
                   if orbit_rows[m][cell]["verdict"] == gold_verdict_of_cell[cell])
        t[m] = corr / len(a_union)
    t_k = t[0]                       # member 0 = identity = K
    ge = sum(1 for m in members if t[m] >= t_k)
    gt = sum(1 for m in members if t[m] > t_k)
    return {"a_union": a_union, "cshuf_active_n": len(a_union),
            "cshuf_orbit_p": ge / len(members), "cshuf_rank": gt + 1,
            "t_identity": t_k, "n_members": len(members),
            "t_min": min(t.values()), "t_max": max(t.values())}


def _write_module(d, recs):
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.json"):
        old.unlink()
    for rec in recs:
        name = re.sub(r"[^a-z0-9.-]+", "-", rec["subject"].split(":")[-1].lower())
        (d / ("%s.json" % name)).write_text(
            json.dumps(rec, indent=1, sort_keys=True) + "\n")


# [R1/R2] 6 scored arms (the single-rotation K-shuf arm is retired; the
# C-SHUF orbit is a 960-member control-evaluation set, not an arm) + oracle.
ARM_NAMES = ("K", "K-lemma-dom", "K-lemma-union",
             "D-word-dom", "D-word-union", "B-wn")


def arm_tbox_paths(arms_dir):
    classes = MODULE / "classes"
    return {
        "K": [classes, MODULE / "kernel"],
        "K-lemma-dom": [classes, arms_dir / "klemma-dom"],
        "K-lemma-union": [classes, arms_dir / "klemma-union"],
        "D-word-dom": [classes, arms_dir / "dword-dom"],
        "D-word-union": [classes, arms_dir / "dword-union"],
        "B-wn": [classes, arms_dir / "bwn"],
    }


def arm_relation(arm, item, minted):
    """The source-side sense projection (design §1.4, grade S; ASM-2101):
    EVERY arm receives the identical item record including the gold sense
    tag. K and B-wn route by it mechanically (K -> NONE on excluded senses
    = fail-closed refusal); the per-lemma inventories (K-lemma-*, D-word-*)
    are constitutively constant in the tag — it is received but has nowhere
    to route (verified by the PC-4' sense-tag insensitivity canary)."""
    s = item["gold_synset"]
    if arm == "K":
        sense = minted.get(s)
        return "urn:%s" % sense.split("urn:")[-1] if sense else None
    if arm == "K-lemma-dom":
        return "urn:kot-engineinf:klemdom:%s" % item["lemma"]
    if arm == "K-lemma-union":
        return "urn:kot-engineinf:klemun:%s" % item["lemma"]
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
    wn_cls = wn_kind_cls(wn, item["object_noun"])
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
