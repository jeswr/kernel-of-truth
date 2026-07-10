#!/usr/bin/env python3
"""knull — plain-store linter (pre-freeze gate G-1 of
docs/design-knull-content-injection-ablation.md section 6.2).

Validates the AUTHORED plain-dictionary definition set
(poc/knull/inputs/plain-authored.json) against the 108 covered concepts.
Every check is fail-closed and named; the same checks are re-run by
build_inputs.py at build time so a store that fails the lint can never be
built into item files.

Checks (G-1 verbatim: LC1, +/-25 percent length band, >=2 segments,
uniqueness, no NSM-legal syntax, authoring-source disclosure):

  L-1  completeness        exactly the 108 covered labels, no extras
  L-2  LC1 own-label       neither the full label nor its headword (first
                           token) occurs as a word in the definition
                           (STRICTER than build-dqar LC1, which checks the
                           full label only)
  L-3  word band           word count within the build band vs the NSM gloss:
                           wc*(1-0.25) <= wn <= max(wc*(1+0.25), wc+8)
  L-4  segments            >=2 admissible claim segments (split on [.;],
                           >=15 chars, no double quotes) — the claim-item
                           contract of build-dqa/build-dqar
  L-5  uniqueness          definitions pairwise distinct AND distinct from
                           every canonical gloss
  R-1  no-verbatim-NSM     no admissible segment of a definition occurs as a
                           substring of ANY canonical gloss (normalized,
                           casefolded), and no canonical-gloss segment occurs
                           in any definition (the attack-9
                           no-verbatim-NSM-line check)
  R-2  register            'zero NSM-legal syntax', operationalized: every
                           admissible segment contains >=1 content token
                           OUTSIDE the NSM-legal surface vocabulary (the 65
                           profile-1 prime exponents + inflections per
                           encoder/src/lexicon.ts, closed English function
                           words, and the 108 concept headwords, which NSM
                           molecule glosses may lawfully use), AND the
                           whole-definition non-NSM content ratio clears
                           REGISTER_RATIO_MIN — canonical NSM glosses sit
                           near 0 on this metric by construction
  R-3  own-gloss overlap   token-set Jaccard(definition, own NSM gloss) <
                           0.5 (the LC3 threshold, reused)
  R-4  hygiene             ASCII only; no double-quote characters; no
                           account-identifying strings (RT-14 pattern list)
  D-1  disclosure          authoring_disclosure block present with fork,
                           drafted_by, drafting_model_family, register, date

Usage:
  python3 poc/knull/lint_plain_store.py            # lint, exit 0/1
  python3 poc/knull/lint_plain_store.py --report   # + per-check summary JSON
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
AUTHORED_PATH = os.path.join(HERE, "inputs", "plain-authored.json")

WORDBAND_FRAC = 0.25
MIN_SEGMENT_CHARS = 15
JACCARD_MAX = 0.5
REGISTER_RATIO_MIN = 0.25   # calibrated: canonical NSM glosses score ~0.0-0.1

TOKEN_RE = re.compile(r"[a-z]+")

# NSM-legal surface vocabulary: English exponents + common inflections of the
# 65 profile-1 primes (encoder/src/lexicon.ts PRIMES), plus closed English
# function words the NSM carrier syntax uses. Concept headwords (molecule
# vocabulary, lawful in molecules-v0 grounding notes) are added at runtime.
NSM_PRIME_SURFACE = {
    # substantives
    "i", "me", "you", "someone", "something", "somethings", "thing", "things",
    "people", "body", "bodies",
    # relational substantives
    "kind", "kinds", "part", "parts",
    # determiners / quantifiers
    "this", "these", "that", "those", "same", "other", "others", "else",
    "another", "one", "two", "some", "all", "much", "many", "little", "few",
    # evaluators / descriptors
    "good", "bad", "big", "small",
    # mental predicates
    "think", "thinks", "thinking", "thought", "know", "knows", "knew",
    "known", "want", "wants", "wanted", "feel", "feels", "felt", "see",
    "sees", "saw", "seen", "hear", "hears", "heard",
    # speech
    "say", "says", "said", "saying", "word", "words", "true",
    # actions, events, movement
    "do", "does", "did", "doing", "done", "happen", "happens", "happened",
    "happening", "move", "moves", "moved", "moving",
    # location, existence, possession
    "be", "is", "are", "am", "was", "were", "being", "been", "there", "mine",
    # life and death
    "live", "lives", "lived", "living", "die", "dies", "died",
    # time
    "when", "time", "times", "now", "before", "after", "long", "short",
    "moment", "moments",
    # space
    "where", "place", "places", "here", "above", "below", "far", "near",
    "side", "sides", "inside", "touch", "touches", "touched",
    # logical
    "not", "no", "maybe", "can", "cannot", "could", "because", "if",
    # intensifier / augmentor / similarity
    "very", "more", "like", "as", "way", "ways",
}

FUNCTION_WORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "with", "and", "or",
    "it", "its", "they", "them", "their", "he", "she", "his", "her", "him",
    "who", "whom", "whose", "what", "which", "will", "would", "from", "for",
    "about", "out", "into", "up", "down", "than", "then", "so", "such",
    "may", "might", "must", "shall", "should", "have", "has", "had",
    "having", "by", "over", "under", "off", "again", "only", "also", "but",
    "any", "each", "every", "none", "nothing", "don", "doesn", "didn",
    "won", "isn", "aren", "wasn", "t", "s", "my", "our", "your", "yes",
    # explication variable letters (kot-axiom carrier syntax, NSM-legal)
    "x", "y", "z",
}

# RT-14 account-string patterns (kot_common.ACCOUNT_PATTERNS, restated here so
# the linter has no import dependency on tools/registry/).
ACCOUNT_RES = (
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"jeswr", re.IGNORECASE),
    re.compile(r"github\.com/[A-Za-z0-9_.-]+"),
    re.compile(r"sparq-org[/#]"),
)


def word_count(text):
    return len(text.split())


def tokens(text):
    return set(TOKEN_RE.findall(text.lower()))


def word_in(word, text):
    return re.search(r"\b%s\b" % re.escape(word.lower()), text.lower()) is not None


def segments(gloss):
    out = []
    for seg in re.split(r"[.;]", gloss):
        seg = seg.strip()
        if len(seg) >= MIN_SEGMENT_CHARS and '"' not in seg and seg not in out:
            out.append(seg)
    return out


def norm(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def load_concepts():
    """Covered concepts via the builder's loader (single source of truth)."""
    sys.path.insert(0, HERE)
    import build_inputs
    return build_inputs.load_covered()


def lint(authored, concepts, findings):
    defs = authored.get("definitions", {})
    labels = [c["label"] for c in concepts]
    by_label = {c["label"]: c for c in concepts}

    # D-1 disclosure
    disc = authored.get("authoring_disclosure") or {}
    for field in ("fork", "drafted_by", "drafting_model_family", "register",
                  "date"):
        if not disc.get(field):
            findings.append(("KNULL_LINT_D1_DISCLOSURE",
                             "authoring_disclosure missing %r" % field))

    # L-1 completeness
    missing = sorted(set(labels) - set(defs))
    extra = sorted(set(defs) - set(labels))
    if missing:
        findings.append(("KNULL_LINT_L1_COMPLETENESS",
                         "missing definitions: %s" % ", ".join(missing[:5])))
    if extra:
        findings.append(("KNULL_LINT_L1_COMPLETENESS",
                         "unknown labels: %s" % ", ".join(extra[:5])))
    if missing or extra:
        return {}

    nsm_available = set(NSM_PRIME_SURFACE) | set(FUNCTION_WORDS)
    for lab in labels:
        nsm_available |= tokens(lab.split(" (")[0])

    canon_glosses = {c["label"]: c["gloss"] for c in concepts}
    canon_norm = {lab: norm(g) for lab, g in canon_glosses.items()}
    canon_segs = {lab: [norm(s) for s in segments(g)]
                  for lab, g in canon_glosses.items()}

    seen = {}
    ratios = {}
    for lab in labels:
        d = defs[lab]
        c = by_label[lab]

        # R-4 hygiene
        try:
            d.encode("ascii")
        except UnicodeEncodeError:
            findings.append(("KNULL_LINT_R4_ASCII", "%s: non-ASCII byte" % lab))
        if '"' in d:
            findings.append(("KNULL_LINT_R4_QUOTE", "%s: double quote" % lab))
        for rx in ACCOUNT_RES:
            if rx.search(d):
                findings.append(("KNULL_LINT_R4_ACCOUNT",
                                 "%s: account-identifying string" % lab))

        # L-2 LC1 own-label (full label AND headword)
        head = lab.split()[0]
        for probe in {lab, head}:
            if word_in(probe, d):
                findings.append(("KNULL_LINT_L2_LC1",
                                 "%s: own label token %r in definition"
                                 % (lab, probe)))

        # L-3 word band
        wc, wn = word_count(c["gloss"]), word_count(d)
        lo, hi = wc * (1 - WORDBAND_FRAC), max(wc * (1 + WORDBAND_FRAC), wc + 8)
        if not (lo <= wn <= hi):
            findings.append(("KNULL_LINT_L3_WORDBAND",
                             "%s: %d words vs NSM %d (band %.1f..%.1f)"
                             % (lab, wn, wc, lo, hi)))

        # L-4 segments
        segs = segments(d)
        if len(segs) < 2:
            findings.append(("KNULL_LINT_L4_SEGMENTS",
                             "%s: %d admissible segments (<2)" % (lab, len(segs))))

        # L-5 uniqueness
        if d in seen:
            findings.append(("KNULL_LINT_L5_DUP",
                             "%s duplicates %s" % (lab, seen[d])))
        seen[d] = lab
        if norm(d) in canon_norm.values():
            findings.append(("KNULL_LINT_L5_DUP",
                             "%s equals a canonical gloss" % lab))

        # R-1 no-verbatim-NSM-line (both directions)
        for seg in segs:
            ns = norm(seg)
            for clab, cg in canon_norm.items():
                if ns in cg:
                    findings.append(("KNULL_LINT_R1_VERBATIM",
                                     "%s: segment %r occurs in canonical %s"
                                     % (lab, seg[:40], clab)))
        dn = norm(d)
        for clab, csegs in canon_segs.items():
            for cs in csegs:
                if cs in dn:
                    findings.append(("KNULL_LINT_R1_VERBATIM",
                                     "%s: canonical %s segment %r occurs in "
                                     "definition" % (lab, clab, cs[:40])))

        # R-2 register (no NSM-legal syntax)
        toks_all = TOKEN_RE.findall(d.lower())
        non_nsm = [t for t in toks_all if t not in nsm_available]
        ratio = len(non_nsm) / float(len(toks_all)) if toks_all else 0.0
        ratios[lab] = round(ratio, 4)
        if ratio < REGISTER_RATIO_MIN:
            findings.append(("KNULL_LINT_R2_REGISTER",
                             "%s: non-NSM content ratio %.3f < %.2f"
                             % (lab, ratio, REGISTER_RATIO_MIN)))
        for seg in segs:
            seg_toks = TOKEN_RE.findall(seg.lower())
            if not any(t not in nsm_available for t in seg_toks):
                findings.append(("KNULL_LINT_R2_REGISTER",
                                 "%s: segment %r has no non-NSM content token"
                                 % (lab, seg[:40])))

        # R-3 own-gloss overlap
        j = jaccard(tokens(d), tokens(c["gloss"]))
        if j >= JACCARD_MAX:
            findings.append(("KNULL_LINT_R3_JACCARD",
                             "%s: Jaccard vs own NSM gloss %.3f >= %.2f"
                             % (lab, j, JACCARD_MAX)))
    return ratios


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="print a per-check summary JSON on success")
    args = ap.parse_args()

    with open(AUTHORED_PATH, encoding="utf-8") as f:
        authored = json.load(f)
    concepts = load_concepts()
    findings = []
    ratios = lint(authored, concepts, findings)

    if findings:
        for code, msg in findings:
            sys.stderr.write("FAIL %s: %s\n" % (code, msg))
        sys.stderr.write("lint_plain_store: %d violation(s)\n" % len(findings))
        sys.exit(1)

    if args.report:
        vals = sorted(ratios.values())
        print(json.dumps({
            "checks": ["D-1", "L-1", "L-2", "L-3", "L-4", "L-5",
                       "R-1", "R-2", "R-3", "R-4"],
            "n_definitions": len(ratios),
            "register_ratio_min_observed": vals[0] if vals else None,
            "register_ratio_median": vals[len(vals) // 2] if vals else None,
            "register_ratio_threshold": REGISTER_RATIO_MIN,
        }, indent=1, sort_keys=True))
    print("lint_plain_store: PASS (108 definitions, all checks green)")


if __name__ == "__main__":
    main()
